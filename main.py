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
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
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

@app.before_request	
def require_login():
    allowed_routes = ['login', 'signup'] 
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['email'] = email
            flash("Logged in.", 'success')
            return redirect('/')
        else:
            flash("User password incorrect or user does not exist.", 'error')
    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])
def user_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return render_template('/')
        else:
            # TODO - create better error message
            return '<h1>Duplicate user exists!</h1>'
    return render_template("signup.html")

@app.route("/logout", methods=['POST'])
def logout():
    del session['email']
    return redirect('/')

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

            blog = Blog(new_title, new_body)
            db.session.add(blog)
            db.session.commit()
            id = str(blog.id)
            return redirect('/post?id='+ id)

@app.route("/")
def index():
    posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', heading="Build a Blog", posts=posts)

if __name__ == "__main__":
    app.run()
