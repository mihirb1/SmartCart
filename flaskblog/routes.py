import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
# from __init__.py file, we do not need to specify file name
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, InputClassesForm
from flaskblog.models import Products, User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
   # uses URL link (ex. ?page=2)
   page = request.args.get('page', 1, type = int)
   # paginate website (newest posts first)
   posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page = 5)
   return render_template('home.html', posts=posts)


@app.route("/about")
def about():
   return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
   if current_user.is_authenticated:
       return redirect(url_for('home'))
   form = RegistrationForm()
   # if user enters valid information into registration form, display success message
   if form.validate_on_submit():
       hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
       # save user's information, but with hashed password before adding to database
       user = User(username = form.username.data, email = form.email.data, password = hashed_password)
       db.session.add(user)
       db.session.commit()
       flash('Your account has been created! You are now able to log in', 'success')
       return redirect(url_for('login'))
       # redirect user to the home page


   return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
   if current_user.is_authenticated:
       return redirect(url_for('home'))
   form = LoginForm()
   if form.validate_on_submit():
        # verify login by checking if database has matching email/pw
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if we are trying to access account and login in is succesful
            # go to account page else go to home page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('input_classes'))
           # for unsuccessful login, use bootstrap's alert message template
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
   return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    # randomize picture name to avoid collisions with same image in folder
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # add saved profile pictures to profile_pics folder
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)


    # resize large pictures
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
   
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
# user must be logged in to access website, managed in __init__ py
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # current_user is logged in user in session, while form is data entered in form
        # update values of user in database (POST request)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        # prefill data when website is loaded (GET request)
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account',
                           image_file = image_file, form = form)


# allows users to go to specific post
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post)


# to update post, you must be logged in
@login_required
@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        # update values in database  
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        # if we are on update page, fill in w/current title/content
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title = 'Update Post',
                           form=form, legend = 'Update Post')


# to update post, you must be logged in
@login_required
@app.route("/post/<int:post_id>/delete", methods = ['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


# shows post for specific username if post author is clicked on
@app.route("/user/<string:username>")
def user_posts(username):
   # uses URL link (ex. ?page=2)
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
   # paginate website (newest posts first)
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    # create email w/subject line, sender, recipients, and message
    msg = Message('Password Reset Request',
                  sender = 'noreply@demo.com',
                  recipients = [user.email])
    msg.body  = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}


If you did not make this request, then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():
    # ensure user is logged out before resetting password
    if current_user.is_authenticated:
       return redirect(url_for('home'))
    form = RequestResetForm()
    # if email is submitted in form
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)


# reset password using token received in email
@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
       hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
       # save user's information, but with hashed password before adding to database
       user.password = hashed_password
       db.session.commit()
       flash('Your password has been updated! You are now able to log in', 'success')
       return redirect(url_for('login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)

@app.route("/input_classes", methods=['GET', 'POST'])
def input_classes():
   
    form = InputClassesForm()
    # if user enters valid information into registration form, display success message
    if form.validate_on_submit():
       if form.class_name.data != "":
           return redirect(url_for('amazon', search=form.class_name.data))
       else:
           return redirect(url_for('amazon', search=form.term.data))
    return render_template('input_classes.html', title='Input Classes', form=form)

@app.route("/amazon", methods = ['GET', 'POST'])
@login_required
def amazon():
    searchQuery = request.args.get('search')
    print(searchQuery)
    products = Products.query.filter(Products.title.like(f"%{searchQuery}%")).filter(Products.unit!="unknown").order_by(Products.total_price.asc()).limit(5).all()
    # displays all products with specific search
    #products = Products.query.filter(Products.title.like(f"%{searchQuery}%")).filter(Products.unit!="unknown").order_by(Products.total_price.asc()).all()
    return render_template('amazon.html', title='Amazon Products', products=products)
