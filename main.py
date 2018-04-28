from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)    #Pass flask app to create DB object to interface with DB using Python code
app.secret_key = 'gl0vxkmaBQmVBGlJRN3eVypaULQKip1utAlI7xZk1QtRHIsJGDPNQE2AhwBoZkpyfZhwQP'   #Allows "session" to function


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(480))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Post Title: %r>' % self.title 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.email


#Validation functions
def is_password(password):

    #Check length of password
    if len(password) < 3 or len(password) > 20:
        return False
    #Check for spaces in password
    for char in password:
        if char == ' ':
            return False
    return True

def is_email(email):
    period_bool = False
    at_bool = False
    #If no email entered set to true
    if email == '' or email == " ":
        return True
    
    #Check email address
    for char in email.strip():
        #Verify no spaces
        if char == ' ':
            return False
        #Verify '.'
        if char == '.':
            period_bool = True
        #Verify @ symbol
        if char == '@':
            at_bool = True
    if period_bool == True and at_bool == True:
        return True
    #If no period or no @ then return False
    return False

#Investigate why this always creates an infinite loop

endpoints_without_login = ['signup','login']

#@app.before_request
#def require_login():
#    if not ('user' in session or request.endpoint in endpoints_without_login):
#        return redirect("/signup")


#Delete current user's email from session[] to logout
@app.route('/logout')
def logout():
    del session['user']
    flash("Logged out")
    return redirect('/')


@app.route('/signup', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if is_email(email) and is_password(password):
            if password == request.form['verify']:
                #Add user(email, password) to the DB
                new_user = User(email, password)

                db.session.add(new_user)
                db.session.commit()
                #Add user to session[] (login)
                session['user'] = email
        
                return redirect('/')
        flash('Email/Password combination invalid')

    elif request.method == 'GET':
        return render_template('signup.html', page_title='Sign Up!')
        


@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html', page_title='Log In!')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = email
                flash('Welcome back, ' + user.email)
                return redirect('/')
        flash('Bad username or password.')
        redirect('/login')


    
#Shows all blog posts
@app.route("/blog", methods=["POST","GET"])
def blog():

    if request.method == "POST":
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        new_blog = Blog(blog_title, blog_body, session['user'])
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()

    blog_id = request.args.get('blog_id')
    if blog_id:
        blogs = Blog.query.filter_by(id=int(blog_id)).all()
        return render_template('blog.html', blogs = blogs, page_title = blogs[0].title)
    else:
        return render_template('blog.html', blogs = blogs, page_title='Build a Blog')


#Allows user to make new blogpost   
@app.route("/newpost", methods=["POST","GET"])
def newpost():
    
    if request.method == "POST":
        title = request.form['blog_title']
        body = request.form['blog_body']

        #Validate input data
        if title == '' or title == ' ':
            flash("Please enter a blog title", "title_error")
        if body == '' or body == ' ':
            flash("Please enter a post for your blog", "body_error")
        if body == '' or body == ' ' or title == '' or title == ' ':
            return redirect('/newpost')
            
        #Create and save Blog object to DB
        new_blog = Blog(title, body, session['user'])
        db.session.add(new_blog)
        db.session.commit()

        #Once post is completed route to that blog's screen
        blogs = Blog.query.all()
        new_blog_id = len(blogs)

        return redirect('/blog?blog_id='+str(new_blog_id))
    
    return render_template('newpost.html', page_title='Add a Blog Entry', blog_body_chars='480')


@app.route("/", methods=["POST","GET"])
def index():

    owner = User.query.filter_by(email=session['user']).first()


    return render_template('blog.html', blogs = blogs, page_title = blogs[0].title)


if __name__ == '__main__':
    app.run()