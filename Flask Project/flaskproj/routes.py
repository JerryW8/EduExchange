from flask import render_template, url_for, flash, redirect, request, abort
from flaskproj import app, db, bcrypt
from flaskproj.forms import RegistrationForm, LoginForm, UpdateAccountForm, SellForm, SwapForm
from flaskproj.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
import re

SWAP_POST = -1
SELL_POST = ""

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
	if request.method == "POST":
		query = request.form["query"]
		return redirect(url_for('search_posts', query=query))
	
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template("home.html", posts=posts) 	# posts will be available in home.html template
   

@app.route("/about")
def about():
	return render_template("about.html", title="About")


@app.route("/register", methods=['GET', 'POST'])
def register():
	
	# if user is already logged in, go back to home page if they try to register
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	
	form = RegistrationForm()
   
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')       # hashing given password
		user = User(username=form.username.data, email=form.email.data, password=hashed_password) # creating new user
		db.session.add(user)
		db.session.commit()
      
		flash(f"Account created for {form.username.data}! You can now log in.", "success")
		return redirect(url_for("login"))
   
	return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
	
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	
	form = LoginForm()
   
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()

		# if user exists and password entered matches, go to home.
		# otherwise, flash error message and go back to login
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')	# if next exists, next_page = the route, else = None
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash("Login Unsuccessful. Please check email and password", "danger")

	return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_profile_pic(form_picture):
	random_hex = secrets.token_hex(8)					# randomizing filename to prevent clash with saved pictures
	_, f_ext = os.path.splitext(form_picture.filename)	# saving file extension
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	
	# rescaling large images
	output_size = (125, 125)			
	i = Image.open(form_picture)
	i.thumbnail(output_size)	# i is rescaled form_picture

	i.save(picture_path)		# saves picture according to path
	
	return picture_fn


def save_post_pic(form_picture):
	random_hex = secrets.token_hex(8)					# randomizing filename to prevent clash with saved pictures
	_, f_ext = os.path.splitext(form_picture.filename)	# saving file extension
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/item_pics', picture_fn)

	i = Image.open(form_picture)
	
	i.save(picture_path)
	
	return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()

	# if info entered in form is valid, we update info and redirect to account page
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_profile_pic(form.picture.data)
			current_user.image_file = picture_file
		
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	# current username and email will be there initially
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	
	image_file = url_for('static', filename= 'profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

# ------- NEW POSTS ----------

@app.route("/sell/new", methods=['GET', 'POST'])
@login_required
def new_sell():
	form = SellForm()
 
	if form.validate_on_submit():
		picture_file = save_post_pic(form.picture.data)
		post = Post(name=form.name.data, price=form.price.data, desc=form.desc.data,
						textbook=form.textbook.data, notes=form.notes.data, electronics=form.electronics.data,
						stationery=form.stationery.data, clothing=form.clothing.data, other=form.other.data,
						location=form.location.data, contact=form.contact.data, more=form.more.data,
						image_file=picture_file, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your sell post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_sell_post.html', title='New Sell Post', form=form, legend='New Sell Post')


@app.route("/swap/new", methods=['GET', 'POST'])
@login_required
def new_swap():
	form = SwapForm()
 
	if form.validate_on_submit():
		picture_file = save_post_pic(form.picture.data)
		post = Post(name=form.name.data, want=form.want.data, desc=form.desc.data,
						textbook=form.textbook.data, notes=form.notes.data, electronics=form.electronics.data,
						stationery=form.stationery.data, clothing=form.clothing.data, other=form.other.data,
						location=form.location.data, contact=form.contact.data, more=form.more.data,
						image_file=picture_file, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your swap post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_swap_post.html', title='New Swap Post', form=form, legend='New Swap Post')

# ------- POST IDs ----------

@app.route("/sell/<int:post_id>")
def sell_post(post_id):
	post = Post.query.get_or_404(post_id)
	# if post is a swap post, then 404
	if post.price == SWAP_POST:
		abort(404)
	return render_template('sell_post.html', post=post)


@app.route("/swap/<int:post_id>")
def swap_post(post_id):
	post = Post.query.get_or_404(post_id)
	# if post is a sell post, then 404
	if post.want == SELL_POST:
		abort(404)
	return render_template('swap_post.html', post=post)

# ------- UPDATE POSTS ----------

@app.route("/sell/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_sell(post_id):
	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403)
	elif post.price == SWAP_POST:
		abort(404)

	form = SellForm()
	
	try:
		if form.validate_on_submit():
			post.name=form.name.data
			post.price=form.price.data
			post.desc=form.desc.data
			post.textbook=form.textbook.data
			post.notes=form.notes.data
			post.electronics=form.electronics.data
			post.stationery=form.stationery.data
			post.clothing=form.clothing.data
			post.other=form.other.data
			post.location=form.location.data
			post.contact=form.contact.data
			post.more=form.more.data
			post.image_file=save_post_pic(form.picture.data)
			db.session.commit()
			flash('Your post has been updated!', 'success')
			return redirect(url_for('sell_post', post_id=post.id))
		elif request.method == 'GET':
			form.name.data = post.name
			form.price.data = post.price
			form.desc.data = post.desc
			form.textbook.data = post.textbook
			form.notes.data = post.notes
			form.electronics.data = post.electronics
			form.stationery.data = post.stationery
			form.clothing.data = post.clothing
			form.other.data = post.other
			form.location.data = post.location
			form.contact.data = post.contact
			form.more.data = post.more
	except:
		flash('Please upload an image file!', 'danger')

	return render_template('create_sell_post.html', title='Update Post', form=form, legend='Update Sell Post')


@app.route("/swap/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_swap(post_id):
	post = Post.query.get_or_404(post_id)

	if post.author != current_user:
		abort(403)
	elif post.want == SELL_POST:
		abort(404)

	form = SwapForm()
	
	try:
		if form.validate_on_submit():
			post.name=form.name.data
			post.want=form.want.data
			post.desc=form.desc.data
			post.textbook=form.textbook.data
			post.notes=form.notes.data
			post.electronics=form.electronics.data
			post.stationery=form.stationery.data
			post.clothing=form.clothing.data
			post.other=form.other.data
			post.location=form.location.data
			post.contact=form.contact.data
			post.more=form.more.data
			post.image_file=save_post_pic(form.picture.data)
			db.session.commit()
			flash('Your post has been updated!', 'success')
			return redirect(url_for('swap_post', post_id=post.id))
		elif request.method == 'GET':
			form.name.data = post.name
			form.want.data = post.want
			form.desc.data = post.desc
			form.textbook.data = post.textbook
			form.notes.data = post.notes
			form.electronics.data = post.electronics
			form.stationery.data = post.stationery
			form.clothing.data = post.clothing
			form.other.data = post.other
			form.location.data = post.location
			form.contact.data = post.contact
			form.more.data = post.more
	except:
		flash('Please upload an image file!', 'danger')

	return render_template('create_swap_post.html', title='Update Post', form=form, legend='Update Swap Post')

# ------- DELETING POSTS ----------

@app.route("/sell/<int:post_id>/delete", methods=['GET','POST'])
@login_required
def delete_sell(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	elif post.price == SWAP_POST:
		abort(404)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))


@app.route("/swap/<int:post_id>/delete", methods=['GET','POST'])
@login_required
def delete_swap(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	elif post.want == SELL_POST:
		abort(404)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))

# ------- SELECT SPECIFIC POSTS ----------

@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()	# get first user w/ username, or 404
	posts = Post.query.filter_by(author=user)\
			.order_by(Post.date_posted.desc())\
			.paginate(page=page, per_page=5)
	return render_template("user_posts.html", user=user, posts=posts)


@app.route("/search/<string:query>")
def search_posts(query):
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter(Post.name.contains(query)).\
			order_by(Post.date_posted.desc()).\
			paginate(page=page, per_page=5)
	return render_template("search_posts.html", posts=posts, query=query)


@app.route("/type/<string:type>")
def type_posts(type):
	page = request.args.get('page', 1, type=int)
	
	if type == "textbooks":
		posts=filter_textbooks(page)
	elif type == "notes":
		posts=filter_textbooks(page)
	elif type == "electronics":
		posts=filter_electronics(page)
	elif type == "stationery":
		posts=filter_stationery(page)
	elif type == "clothing":
		posts=filter_clothing(page)
	elif type == "other":
		posts=filter_other(page)
	else:
		abort(404)

	return render_template("type_posts.html", posts=posts, type=type)


def filter_textbooks(page):
	filtered_posts = Post.query.filter_by(textbook=True)\
					.order_by(Post.date_posted.desc())\
					.paginate(page=page, per_page=5)
	return filtered_posts


def filter_notes(page):
	filtered_posts = Post.query.filter_by(note=True)\
					.order_by(Post.date_posted.desc())\
					.paginate(page=page, per_page=5)
	return filtered_posts


def filter_electronics(page):
	filtered_posts = Post.query.filter_by(electronics=True)\
					.order_by(Post.date_posted.desc())\
					.paginate(page=page, per_page=5)
	return filtered_posts


def filter_stationery(page):
	filtered_posts = Post.query.filter_by(stationery=True)\
					.order_by(Post.date_posted.desc())\
					.paginate(page=page, per_page=5)
	return filtered_posts


def filter_clothing(page):
	filtered_posts = Post.query.filter_by(clothing=True)\
					.order_by(Post.date_posted.desc())\
					.paginate(page=page, per_page=5)
	return filtered_posts


def filter_other(page):
	filtered_posts = Post.query.filter_by(other=True)\
					.order_by(Post.date_posted.desc())\
					.paginate(page=page, per_page=5)
	return filtered_posts