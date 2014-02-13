from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid, functions
from forms import LoginForm, EditForm, QuestionForm, AnalyseForm, NewsletterForm, TagForm
from models import User, ROLE_USER, ROLE_ADMIN, Log, Query, Tag
from datetime import datetime
from flask.ext.moment import Moment
from SPARQLWrapper import SPARQLWrapper, JSON

import gspread
import quepy
import urllib
import re, os
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from sqlalchemy import desc


@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()

@app.errorhandler(404)
def internal_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500


@app.route('/index')
@login_required
def index():
	user = g.user
	posts = [
		{ 
			'author': { 'nickname': 'John' }, 
			'body': 'Beautiful day in Portland!' 
		},
		{ 
			'author': { 'nickname': 'Susan' }, 
			'body': 'The Avengers movie was so cool!' 
		}
	]
	return render_template('index.html',
		title = 'Home',
		user = user,
		posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('query'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
	return render_template('login.html', 
		title = 'Sign In',
		form = form,
		providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
	allowed = app.config['ALLOWED_USERS']
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	elif len(set(allowed).intersection(set([resp.email]))):
		user = User.query.filter_by(email = resp.email).first()
		if user is None:
			nickname = resp.nickname
			if nickname is None or nickname == "":
				nickname = resp.email.split('@')[0]
			nickname = User.make_unique_nickname(nickname)
			user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
			db.session.add(user)
			db.session.commit()
		remember_me = False
		if 'remember_me' in session:
			remember_me = session['remember_me']
			session.pop('remember_me', None)
		login_user(user, remember = remember_me)
		return redirect(request.args.get('next') or url_for('query', user=g.user))
	else:
		flash("Sorry we're accepting beta invites only at this stage "+resp.email)
		return redirect(url_for('home', user=g.user))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))
	
@app.route('/user/<nickname>')
@login_required
def user(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	now = datetime.utcnow()
	if user == None:
		flash('User ' + nickname + ' not found.')
		return redirect(url_for('query'))
	
	logs = Log.query.all()
	return render_template('user.html', user = user, logs=logs, now=now)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		g.user.about_me = form.about_me.data
		db.session.add(g.user)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit'))
	elif request.method != "POST":
		form.nickname.data = g.user.nickname
		form.about_me.data = g.user.about_me
	return render_template('edit.html', form = form, user = g.user)

		

@app.route('/', methods=['GET', 'POST'])
def home():
	g.user = current_user
	form = NewsletterForm(request.form)
	if g.user.is_authenticated():
		return redirect(url_for('query'))
	else:
		if request.method == 'POST' and form.validate():
			gc = gspread.Client(auth=('open.impact.org@gmail.com', '0pen1mpact'))
			gc.login()
			wks = gc.open("user-sign-up").sheet1
			values_list = wks.col_values(1)
			timestamp = datetime.utcnow().strftime('%d-%m-%y')
			wks.append_row([form.email.data, timestamp])
			# flash("You signed up to our beta launch")
			return render_template('home.html', user=g.user)

	return render_template('home.html', user=g.user, form=form)


@app.route('/team')
def team():
	return render_template('team.html', user=g.user)

@app.route("/query", methods = ['GET', 'POST'])
@login_required
def query():
	# Initialise variables // move out of function and make them global?
	query=None
	answer=None
	alert=None
	log=None
	asks = 444
	tag=None
	tags = Tag(None)
	all_tags = []
	tag_list = []
	query_tags =[]
	remaining_tags = []
	existing_query=None
	title=""
	question = request.args.get('question', '')
	tabs = {"results":"", "sparql":"", "meta":"", "talk":""}
	# Initialise form variables
	form = QuestionForm()
	tag_form = TagForm()

	# Checks if the GET value exists
	if question:
		quepy_process = functions.quepyProcess(question)    # Process the quesiton with Quepy
		query, answer = quepy_process[0], quepy_process[1]     # assign results to variables.
		existing_query = Query.query.filter_by(sparql_id = query.sparql_id).first()
		tabs['results'] = "active"
		# check if this sparql query is in the database
		if existing_query:
			query = existing_query
			existing_query.asks += 1
			db.session.commit()
		else:
			query = Query(
			sparql_id = query.sparql_id,
			sparql_code = query.sparql_code,
			question = query.question,
			errors = query.errors,
			votes = query.votes,
			tags = query.tags,
			timestamp = query.timestamp,
			asks = 1,
			success = query.success
			)
			db.session.add(query)
			db.session.commit()        

		title = query.question

		tag_list = [str(child.name) for child in Query.query.filter_by(sparql_id = query.sparql_id).first().tags]
		tag_list = [x+"  x "+str(Tag.query.filter_by(name=x).first().tag_cnt) for x in tag_list]

		if tag_list is None:
			tag_list = []
		
		# Save tags from form
		if request.method == 'POST':
			if tag_form.validate_on_submit():
				
				tabs['results'], tabs['talk'] = "", "active"
				tag_list = [str(child.name) for child in Query.query.filter_by(sparql_id = query.sparql_id).first().tags]
				tag_list = [x+"  x "+str(Tag.query.filter_by(name=x).first().tag_cnt) for x in tag_list]

				form_tags = tag_form.tag.data.split(",")
				tag_form.tag.data = ''
				insert_tags = [tag for tag in form_tags if tag not in tag_list]
				tag_list += [str(tag) for tag in insert_tags if tag !=""]

				for child in insert_tags:
					tag = Tag(child)
					if len(child) >2 and child != "":
						existing_query.tags += [tag]
						db.session.commit()
	
		query_tags = [str(child.name) for child in Tag.query.all()]
		remaining_tags = functions.removeDuplicates([x for x in query_tags if x not in tag_list])

		# Log the query for user logs. (this is doubling up with talk page?)
		log = Log(nlq=query.question, sparql=query.sparql_code, timestamp=query.timestamp, success=query.success, author=g.user)
		db.session.add(log)
		db.session.commit()
		# all_tags = Tag.query.all()
		# tags = [ tag.name for tag in db.session.query(Tag).order_by(Tag.name) ]
	# else:
	# 	alert = "Try again"

	


	return render_template('query.html',
		all_tags=all_tags,
		tag_form = tag_form,
		form = form,
		query=query,
		user=g.user,
		answer=answer,
		alert=alert,
		log=log,
		tag=tag, 
		tag_list = tag_list, 
		query_tags = query_tags,
		remaining_tags = remaining_tags,
		existing_query = existing_query, 
		title= title, 
		now=datetime.utcnow(), 
		tab=tabs)
	



@app.route("/analyse", methods = ['GET', 'POST'])
@login_required
def analyse():
	answer=""
	form = AnalyseForm()
	
	tag={}
	tag['CC']="Coordinating conjunction"
	tag['CD']="Cardinal number"
	tag['DT']="Determiner"
	tag['EX']="Existential there"
	tag['FW']="Foreign word"
	tag['IN']="Preposition or subordinating conjunction"
	tag['JJ']="Adjective"
	tag['JJR']="Adjective, comparative"
	tag['JJS']="Adjective, superlative"
	tag['LS']="List item marker"
	tag['MD']="Modal"
	tag['NN']="Noun, singular or mass"
	tag['NNS']="Noun, plural"
	tag['NNP']="Proper noun, singular"
	tag['NNPS']="Proper noun, plural"
	tag['PDT']="Predeterminer"
	tag['POS']="Possessive ending"
	tag['PRP']="Personal pronoun"
	tag['PRP$']="Possessive pronoun"
	tag['RB']="Adverb"
	tag['RBR']="Adverb, comparative"
	tag['RBS']="Adverb, superlative"
	tag['RP']="Particle"
	tag['SYM']="Symbol"
	tag['TO']="to"
	tag['UH']="Interjection"
	tag['VB']="Verb, base form"
	tag['VBD']="Verb, past tense"
	tag['VBG']="Verb, gerund or present participle"
	tag['VBN']="Verb, past participle"
	tag['VBP']="Verb, non-3rd person singular present"
	tag['VBZ']="Verb, 3rd person singular present"
	tag['WDT']="Wh-determiner"
	tag['WP']="Wh-pronoun"
	tag['WP$']="Possessive wh-pronoun"
	tag['WRB']="Wh-adverb"

	if form.validate_on_submit():
		question = form.question.data

	if os.path.isdir("C:/Users/edanw_000/My Programming libraries/ntlk/"):
		NLTK_DATA_PATH = ["C:/Users/edanw_000/My Programming libraries/ntlk/"]
	elif os.path.isdir("/home/edanweis/webapps/oi3/oi3"):
		NLTK_DATA_PATH = ["/home/edanweis/webapps/oi3/oi3"]
	else:
		answer = "no NLTK found"
	
	try:
		answer = quepy.nltktagger.run_nltktagger(urllib.unquote(question), NLTK_DATA_PATH)
		tokens = []
		tokens_length = len(answer)

		for child in answer:
			token = {}
			token["token"] = str(child.token)
			token["POS"] = str(child.pos)
			token["lema"]= str(child.lemma)
			token["prob"]= str(child.prob)
			tokens.append(token)

		return render_template('analyse.html', form=form, user=g.user, tokens=tokens, answer=answer, tag=tag)

	except:
		if answer == None:
			answer = "Try again"
		pass

	return render_template('analyse.html', form=form, user=g.user, answer=answer)

@app.route('/log')
@login_required
def log():
	logs = Log.query.order_by(desc(Log.timestamp)).all()

	return render_template('log.html', logs=logs, now=datetime.utcnow())    
