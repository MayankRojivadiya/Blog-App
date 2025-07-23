from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'rojivadiyamayankmanojbhai08082005'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash('Email or Username already exists!')
            return redirect('/signup')

        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/dashboard')
        else:
            flash('Invalid username or password')
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user_posts = Post.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', posts=user_posts)

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('new_post.html')

@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != session.get('user_id'):
        flash("You are not authorized to edit this post.")
        return redirect('/dashboard')
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/dashboard')
    return render_template('edit_post.html', post=post)

@app.route('/post/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != session.get('user_id'):
        flash("You are not authorized to delete this post.")
        return redirect('/dashboard')
    db.session.delete(post)
    db.session.commit()
    return redirect('/dashboard')

# -------------------- MAIN --------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)