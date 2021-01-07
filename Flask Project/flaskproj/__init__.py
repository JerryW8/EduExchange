from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '99c00e76755ed8aa9553ae92178fac97'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'    # site.db is created in current directory

db = SQLAlchemy(app)                                           # creating database
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 								# redirect to login if not logged in
login_manager.login_message_category = 'info'					# customizing message

from flaskproj import routes
db.create_all()