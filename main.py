from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


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

    def __init__(self, title, body):
        self.title = title
        self.body = body
    def __repr__(self):
        return '<Post Title: %r>' % self.title 


#Shows all blog posts
@app.route("/blog", methods=["POST","GET"])
def blog():

    if request.method == "POST":
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()

    blog_id = request.args.get('blog_id')
    if blog_id:
        blogs = Blog.query.filter_by(id=int(blog_id)).all()
        return render_template('blog.html', blogs = blogs, page_title = blogs[0].title)

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
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()

        #Once post is completed route to that blog's screen
        blogs = Blog.query.all()
        new_blog_id = len(blogs)

        return redirect('/blog?blog_id='+str(new_blog_id))
    
    return render_template('newpost.html', page_title='Add a Blog Entry', blog_body_chars='480')


@app.route("/", methods=["POST","GET"])
def index():
    return redirect('/blog')


if __name__ == '__main__':
    app.run()