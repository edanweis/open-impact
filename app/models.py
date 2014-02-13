from hashlib import md5
from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import UniqueConstraint, Index

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	log = db.relationship('Log', backref = 'author', lazy = 'dynamic')

	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname = nickname).first() == None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname = new_nickname).first() == None:
				break
			version += 1
		return new_nickname
		
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
		
	def __repr__(self):
		return '<User %r>' % (self.nickname)    
		
class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)

class Log(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nlq = db.Column(db.String(140), nullable=True)
	sparql = db.Column(db.String(140), nullable=True)
	timestamp = db.Column(db.DateTime, nullable=True)
	success = db.Column(db.Boolean, unique=False, nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

	def __repr__(self):
		return '<Log %r>' % (self.nlq)


tags = db.Table('tags',
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), unique=True),
	db.Column('query_id', db.Integer, db.ForeignKey('query.id'))
)

class Query(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	sparql_id = db.Column(db.String(2000), nullable=True)
	sparql_code = db.Column(db.String(2000), nullable=True)
	question = db.Column(db.String(2000), nullable=True)
	errors = db.Column(db.String(140), nullable=True)
	votes = db.Column(db.Integer, nullable=True)
	tags = db.relationship('Tag', secondary=tags, backref=db.backref('queries', lazy='dynamic'))
	timestamp = db.Column(db.DateTime, nullable=True)
	asks = db.Column(db.Integer, nullable=True)
	success = db.Column(db.Boolean, nullable=True, unique=False)    

	def __init__(self, sparql_id=None, sparql_code=None, question = None, errors=None, votes=None, tags=None, timestamp=None, asks=777, success=None):
		self.sparql_id = sparql_id
		self.sparql_code = sparql_code
		self.question = question
		self.errors = errors
		self.votes = votes
		self.tags = tags
		self.timestamp = timestamp
		self.asks = asks
		self.success = success        

	def __repr__(self):
		return '<Query %r, Tags %r>' % (self.sparql_code, self.tags)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=True)
	
	@property
	def tag_cnt(self):
		# Uniqueness work around must solve
		return Tag.query.filter_by(name = self.name).count()
		# return db.session.object_session(self).query(Query).with_parent(self, "queries").count()

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Tag %r>' % self.name

