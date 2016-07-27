from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_searchable import make_searchable
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
import subprocess


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lfcs-test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#path stuff for backups
os.environ['BACKUP_DIR'] = os.path.dirname(os.path.realpath(__file__)) + '/backups'
os.environ['PSQL_DIR'] = subprocess.Popen("which psql", shell=True, stdout=subprocess.PIPE).stdout.read().splitlines()[0]
os.environ['PG_DUMP_DIR'] = subprocess.Popen("which pg_dump", shell=True, stdout=subprocess.PIPE).stdout.read().splitlines()[0]
os.environ['DB_NAME'] = 'lfcs-test'

app.secret_key = "thisisaverysecretkeyyouwillneverguess"

db = SQLAlchemy(app)

#config for search
make_searchable()

db.configure_mappers()
db.create_all()

bcrypt = Bcrypt()
login_manager = LoginManager(app)

import lfcsapp.views
