from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi 

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(256), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

endpoints_without_login = ['newpost']

@app.before_request
def require_login():
    if 'email' not in session and request.endpoint in endpoints_without_login:
        return redirect("/login")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email.strip() == "":
            flash('You must enter a valid username.', 'error')
            return redirect('/login')

        if password.strip() == "":
            flash('You must enter a valid password.', 'error')
            return redirect('/login')

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Welcome back, ' + email + '!', 'success')
            return redirect('/newpost')
        elif user and user.password != password:
            flash("The password you entered is incorrect. Please try again or signup.", 'error')
            return redirect('/login')
        else:
            flash("We're sorry but that user does not exist.", 'error')
            return redirect('/login')
    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])
def user_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if email.strip() == "":
            flash('You must enter a valid username.', 'error')
            return redirect('/sigup')

        if not is_email(email):
            flash('Uh-oh! "' + email + '" does not look like an email address.', 'error')
            return redirect('/signup')

        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('Sorry! "' + email + '" is already a registered user.', 'error')
            return redirect ('/signup')

        if password.strip() == "" or len(password) < 3:
            flash('You must enter a valid password.', 'error')
            return redirect('/sigup')

        if password != verify:
            flash('The passwords you entered do not match', 'error')
            return redirect('/signup')

        new_user = User(email, password)
        db.session.add(new_user)
        db.session.commit()
        session['email'] = email
        flash('Welcome to Bloggz, ' + email + '!', 'success')
        return redirect('/newpost')
    else:
        return render_template("signup.html")

def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST'])
def logout():
    del session['email']
    return redirect('/blogs')

@app.route("/post")
def post():
    id = request.args['id']
    post = Blog.query.filter_by(id=id).first()
    return render_template('post.html', heading="Post Detail", post=post)
 
@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    heading="Add a Blog Entry"
    errors = False
    error1 = ""
    error2 = ""
    if request.method == 'GET':
        return render_template('add.html', heading=heading)
 
    else: 
        new_title = request.form['post-title']
        new_body = request.form['post-body']


        # if the user typed nothing at all, redirect and tell them the error
        if (new_title.strip() == ""):
            error1 = "Please add a title before posting."
            errors = True

        # if the user typed nothing at all, redirect and tell them the error
        if (new_body.strip() == ""):
            error2 = "Please add some content before posting."
            errors = True

        if errors == True:
            return render_template('add.html', heading=heading, error1=error1, error2=error2, title=new_title, body=new_body)

        else:
            owner = User.query.filter_by(email=session['email']).first()
            blog = Blog(new_title, new_body, owner)
            db.session.add(blog)
            db.session.commit()
            id = str(blog.id)
            return redirect('/post?id='+ id)

@app.route("/blog")
def blog():
    user = request.args['user']
    posts = Blog.query.filter_by(owner_id=int(user)).all()
    return render_template('blog.html', heading="Bloggz Entries", posts=posts)

@app.route("/blogs")
def blogs():
    posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', heading="Bloggz Entries", posts=posts)

@app.route("/")
def index():
    authors = User.query.order_by(User.email).all()
    return render_template('index.html', heading="Bloggz Home", authors=authors)

if __name__ == "__main__":
    app.run()
