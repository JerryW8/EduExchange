from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user													
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, NumberRange 	
import email_validator
from flaskproj.models import User, Post
from abc import ABC

class RegistrationForm(FlaskForm):
	username = StringField('Username', 
	    					validators=[DataRequired(), Length(min=2, max=20)])	
	email = StringField('Email',
	    				validators=[DataRequired(), Email()])
	password = PasswordField('Password', 
	    					validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
	    				validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	# takes in username at registration and throws error if it is taken
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		# if not None
		if user:
			raise ValidationError('That username is taken. Please choose a different one')
          
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', 
							validators=[DataRequired(), Length(min=2, max=20)])	
	email = StringField('Email',
						validators=[DataRequired(), Email()])
	picture = FileField('Update Profile Picture', 
						validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
		# if the username is the same, we don't do anything
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one')
          
	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one')


class LoginForm(FlaskForm):
	email = StringField('Email',
						validators=[DataRequired(), Email()])
	password = PasswordField('Password', 
							validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class SellForm(FlaskForm):
	name = StringField('Item Name', validators=[DataRequired()])
	price = DecimalField('Price', places=2, validators=[DataRequired(), 
						NumberRange(min=0.01, message="Price must be at least %(min)")])
	desc = TextAreaField('Item Description', validators=[DataRequired()],
						render_kw={"placeholder":"A brief description of what you are selling..."})
	picture = FileField('Upload image', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
	textbook = BooleanField()
	notes = BooleanField()
	electronics = BooleanField()
	stationery = BooleanField()
	clothing = BooleanField()
	other = BooleanField()
	location = StringField('Location', validators=[DataRequired()],
						render_kw={"placeholder":"123 Main St, Toronto, ON"})
	contact = StringField('Contact', validators=[DataRequired()],
						render_kw={"placeholder":"Phone, email, social media, etc."})
	more = TextAreaField('Additional Info (Optional)',
						render_kw={"placeholder":"Anything else you would like to add..."})
	submit = SubmitField('Post')


class SwapForm(FlaskForm):
	name = StringField('Item Name', validators=[DataRequired()])
	want = TextAreaField('Looking for...', validators=[DataRequired()],
						render_kw={"placeholder":"Please list the items you want in exchange..."})
	desc = TextAreaField('Item Description', validators=[DataRequired()],
						render_kw={"placeholder":"A brief description of what you are swapping..."})
	picture = FileField('Upload image', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
	textbook = BooleanField()
	notes = BooleanField()
	electronics = BooleanField()
	stationery = BooleanField()
	clothing = BooleanField()
	other = BooleanField()
	location = StringField('Location', validators=[DataRequired()],
						render_kw={"placeholder":"123 Main St, Toronto, ON"})
	contact = StringField('Contact', validators=[DataRequired()],
						render_kw={"placeholder":"Phone, email, social media, etc."})
	more = TextAreaField('Additional Info (Optional)',
						render_kw={"placeholder":"Anything else you would like to add..."})
	submit = SubmitField('Post')