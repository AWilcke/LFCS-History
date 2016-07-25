from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_searchable import make_searchable
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lfcs-test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


app.secret_key = "thisisaverysecretkeyyouwillneverguess"

db = SQLAlchemy(app)

#config for search
make_searchable()

db.configure_mappers()
db.create_all()

bcrypt = Bcrypt()
login_manager = LoginManager(app)

import lfcsapp.views
