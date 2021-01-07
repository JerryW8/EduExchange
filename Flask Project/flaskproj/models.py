from datetime import datetime
from flaskproj import db, login_manager
from flask_login import UserMixin

# accesses user by ID
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)   # usernames are unique and cannot be null
	email = db.Column(db.String(120), unique=True, nullable=False)
    
    # users at least have default image. Don't have to be unique since many can share default
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)      # passwords can be same between users
    
    # posts has a relationship to the Post model (class) for user
    #   backref is similar to adding a column to Post
    #   author attribute can be used to access user object who made post
    #   lazy=True means SQLAlchemy will load the data at once (all posts of one user)
	posts = db.relationship('Post', backref='author', lazy=True)
    
    # defines how user object is outputted
	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Float, nullable=False, default=-1)
	want = db.Column(db.Text, nullable=False, default="")
	desc = db.Column(db.Text, nullable=False)
	textbook = db.Column(db.Boolean, nullable=False)
	notes = db.Column(db.Boolean, nullable=False)
	electronics = db.Column(db.Boolean, nullable=False)
	stationery = db.Column(db.Boolean, nullable=False)
	clothing = db.Column(db.Boolean, nullable=False)
	other = db.Column(db.Boolean, nullable=False)
	location = db.Column(db.String(100), nullable=False)
	contact = db.Column(db.Text, nullable=False)
	more = db.Column(db.Text, nullable=False, default="N/A")
	image_file = db.Column(db.String(100), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Post('{self.id}', '{self.name}', '{self.price}', '{self.desc}')"