from flask import Flask, render_template, request,flash, redirect, url_for, session, logging
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField,TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Config MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL

mysql = MySQL(app)


#Articles = Articles()

# Index

@app.route('/')
def index():
	return render_template('home.html')


# About

@app.route('/about')
def about():
	return render_template('about.html')


# Browsing through different artices

@app.route('/articles')
def articles():
	# Create cursor

	cur = mysql.connection.cursor()

	# Get articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result> 0:
		return render_template('articles.html', articles = articles)

	else:
		msg = 'No articles found'
		return render_template('articles.html', msg = msg)
			
	# Close connection

	cur.close()	


# Individual articles

@app.route('/article/<string:id>/')
def article(id):
	# Create cursor

	cur = mysql.connection.cursor()

	# Get articles
	result = cur.execute("SELECT * FROM articles where id= %s", [id])

	articles = cur.fetchall()


	return render_template('articles.html', article = article)

# Registration form class

class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 50)])
	username = StringField('Username', [validators.Length(min =4 ,max = 25)])
	email = StringField('Email', [validators.Length(min = 6 , max = 50)])
	password = PasswordField('Password',
		[validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Wrong Password!'),
		])
	confirm = PasswordField('Confirm Password')

# User Register

@app.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegisterForm(request.form)

	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password =  sha256_crypt.encrypt(str(form.password.data))


		# Create cursor

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)", (name, email, username, password))

		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('You are now registered and can log in', 'success')

		redirect(url_for('index'))

		return  render_template('register.html', form=form)
	return render_template('register.html', form = form)


# Login page

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':

		# Get form fields
		username = request.form['username']
		password_candidate = request.form['password']

		# Create cursor

		cur = mysql.connection.cursor()

		# Get user by Username
		result = cur.execute("SELECT * FROM users where username = %s", [username])

		if result >0:
			# Get stored hash

			data = cur.fetchone()
			password = data['password']

			# Compare passwords

			if sha256_crypt.verify(password_candidate, password):
				# Correct password
				session['logged in'] = True
				session['username'] = username

				flash("You are now logged in!", 'success')

				return redirect(url_for('dashboard'))

			else:
				error = 'Wrong password'
				return render_template('login.html', error= error)
			cur.close()
		else:
			error = 'Username not found'
			return render_template('login.html',error =  error)

	return render_template('login.html')


# Check if user logged in

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):

		if 'logged in' in session: #or session['logged in']==True:
			return f(*args, **kwargs)
		else:
			flash("Unauthorized. Please log in.", 'danger')
			return redirect(url_for('login'))

	return wrap




# Logout

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out!', 'success')
	return redirect(url_for('login'))


# Dashboard

@app.route('/dashboard')
@is_logged_in
def dashboard():
	# Create cursor

	cur = mysql.connection.cursor()

	# Get articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result> 0:
		return render_template('dashboard.html', articles = articles)

	else:
		msg = 'No articles found'
		return render_template('dashboard.html', msg = msg)
			
	# Close connection

	cur.close()	

# Article form class

class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min = 1, max = 200)])
	body = TextAreaField('Body', [validators.Length(min =30)])
	
# Adding a new article

@app.route('/add_article', methods =['GET', 'POST'])

@is_logged_in
def add_article():

	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		# Create Cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

		# Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash('Article Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_article.html', form=form)

if __name__ == '__main__':
	app.secret_key = 'secret123'
	app.run(debug = True)

