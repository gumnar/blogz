from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost/build-a-blog'
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


def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present


#endpoints_without_login = ['signup', 'login', 'blog', '/']

#@app.before_request
#def require_login():
#    if not ('user' in session or request.endpoint in endpoints_without_login):
#        return redirect("/signup")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template('signup.html', page_title='Sign Up!')
    
    elif request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if is_email(email):
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user and password == verify:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['user'] = email
                flash('Hello, '+session['user'])
                return redirect('/blog')
            elif existing_user:
                flash('That email has already been used!', 'error')
                return redirect('/signup')
            else:
                flash('Your passwords must match!','error')
                return redirect('/signup')
        else:
            flash('You must enter a valid email!','error')
            return redirect('/signup')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template('login.html', page_title='Log In!')
    
    elif request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user'] = email
            flash("Welcome back "+session['user'], 'message')
            return redirect('/blog')
        else:
            flash('Username/password combination invalid, please try again', 'error')
            return redirect('/login')


@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    flash("Logged Out")
    return redirect('/blog')


#Shows all blog posts
@app.route("/blog", methods=["POST","GET"])
def blog():

    if request.method == 'GET':
        user_id = request.args.get('userId')
        if user_id:
            owners = User.query.filter_by(id=int(user_id)).all()
            blogs = Blog.query.filter_by(owner_id=owners[0].id).all()
            return render_template('blog.html', blogs=blogs, page_title = owners[0].email, authors = owners)

        blog_id = request.args.get('blog_id')
        if blog_id:
            blogs = Blog.query.filter_by(id=int(blog_id)).all()
            authors = User.query.all()

            return render_template('blog.html', blogs = blogs, page_title = blogs[0].title, authors = authors)

        else:
            return render_template('blog.html', blogs = Blog.query.all(), page_title='All Posts', authors = User.query.all())
        



#Allows user to make new blogpost   
@app.route("/newpost", methods=["POST","GET"])
def newpost():
    
    if request.method == "POST":
        title = request.form['blog_title']
        body = request.form['blog_body']
        
        owner = User.query.filter_by(email=session['user']).first()

        #Validate input data
        if title == '' or title == ' ':
            flash("Please enter a blog title", "title_error")
        if body == '' or body == ' ':
            flash("Please enter a post for your blog", "body_error")
        if body == '' or body == ' ' or title == '' or title == ' ':
            return redirect('/newpost')
            
        #Create and save Blog object to DB
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

        #Once post is completed route to that blog's screen
        blogs = Blog.query.filter_by(owner=owner).all()
        all_blogs = Blog.query.all()
        new_blog_id = len(all_blogs)

        return redirect('/blog?blog_id='+str(new_blog_id))
    
    return render_template('newpost.html', page_title='Add a Blog Entry', blog_body_chars='480')


@app.route("/", methods=["POST","GET"])
def index():
    #If signed in then route to blog and display blogs for user in session
    if request.method == 'GET':
        users = User.query.all()
        return render_template('index.html',users=users, page_title='All Users')

    return redirect('/index')


if __name__ == '__main__':
    app.run()