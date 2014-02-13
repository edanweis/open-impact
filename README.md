

Open Impact
===
### Free and Open Data on the social impact of design
![Open Impact](https://github.com/edanweis/open-impact/raw/master/oi_avatar.jpg)


### Dependencies (see requirements.txt)

* [All of Miguel Grinberg's tutorial dependencies](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
* Flask-Bootstrap==3.0.3.1
* Flask-Moment==0.2.0
* SPARQLWrapper==1.5.2
* gspread==0.1.0
* nltk==2.0.4
* numpy==1.8.0
* quepy==0.2
* rdflib==4.0.1


### Instructions

1. Install Python 2.7 or higher
2. Install module dependencies using: `pip install -r requirements.txt` preferably in a virtual environment. 
3. Install Numpy, then Quepy then NLTK, as per [these instructions](http://quepy.readthedocs.org/en/latest/#installation)
4. Generate an **app.db** file by running `python db_create.py` in the root folder. See [Miguel's notes on app.db](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)
5. The script can simply be executed as follows: `python run.py`
6. Voila! see it at: http://localhost:5000


### Todo: features

Task | Dependencies | Priority
--- | --- | ---
Quepy regex pattern matching | learning | High
Secure Oath / OpenId login |  | High
"About us" page | Photo from Nrupak | Medium
Search by tag | | High


### Todo: bugs/technical changes

Task | why | Priority
--- | --- | ---
Implement Post/Redirect/Get pattern | Prevent form resubmission on reload | High
Use ajax for tags, and profile forms | faster, no page reload necessary | Medium


### Note
This repository contains sensitive information to the Open Impact team, like emails and passwords.