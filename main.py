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
    title = db.Column(db.String(120))
    body = db.Column(db.String(256))

    def __init__(self, title):
        self.name = name
        self.body = body

def get_blog_list():
    return Blog.query.all()


@app.route("/add", methods=['POST'])
def add_post():
    new_title = request.form['post-title']
    new_body = request.form['post-body']

    # if the user typed nothing at all, redirect and tell them the error
    if (not new_title.strip() == "") or (new_body.strip() == ""):
        error = "Please add some content before posting."
        return redirect("/?error=" + error)

    blog = Blog(new_title, new_body)
    db.session.add(blog)
    db.session.commit()
    return render_template('blog.html', blog=blog)

@app.route("/")
def index():
    encoded_error = request.args.get("error")
    return render_template('blog.html', bloglist=get_blog_list(), error=encoded_error and cgi.escape(encoded_error, quote=True), title='Build A Blog')

if __name__ == "__main__":
    app.run()
