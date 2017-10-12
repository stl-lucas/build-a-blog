from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(256), nullable=False)

    def __init__(self, title, body):
        self.title = title
        self.body = body

def get_blog_list():
    return Blog.query.filter_by(id=1).first()


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
		
            return redirect('/post', id=Blog.id)

@app.route("/")
def index():
    posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', heading="Build a Blog", posts=posts)

if __name__ == "__main__":
    app.run()
