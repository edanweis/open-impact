open-impact
===========


If you want to deploy this on your local server, I am using Wampserver and following this tutorial: http://abbett.org/post/setting-up-mod-wsgi-on-wampserver

A wsgi.py file needs to exist in the directory, wsgi.py  Mine looks like this, using a virtualenv "flask" with all requirements installed. 



import sys, os, logging

venv_path = "/home/edanweis/.virtualenvs/flask"
activate_this = os.path.join(venv_path, "bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, '/home/edanweis/webapps/oi3')
sys.path.insert(0, '/home/edanweis/webapps/oi3/oi3')
from app import app as application
logging.basicConfig(stream=sys.stderr) 




Oh boy, this is getting complicated. I'll write some proper instructions soon.