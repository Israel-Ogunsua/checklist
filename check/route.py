from flask.helpers import flash
from check import app
from flask import render_template,url_for,request,flash, redirect
from check import bcrypt
from check.models import User,Post, Archive
from flask_login import login_user, login_required,current_user, logout_user
from check.models import db
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    data = []
    if current_user.is_authenticated:
        user = current_user.get_id()

        users  = User.query.filter_by(id= user)
        for make in users:
            data.append(make.posts)
            
        if request.method == 'POST':
            title  = request.form['fname']
            discription = request.form['disc']
            duetime = request.form['duetime']
            status = request.form['status']

            post = Post(title = title, discription = discription,Duetime= duetime, status = status, user_id = user)
            db.session.add(post)
            db.session.commit()
    else:
        if request.method == 'POST':
           return redirect('login')
    return render_template('index.html', context= data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 == password2:
            hash_pawd= bcrypt.generate_password_hash(request.form['password1']).decode('utf-8')
            users = User(username = username, email = email, password = hash_pawd)
            db.session.add(users)
            db.session.commit()
            return redirect('login')
        else:
            flash("Your password doesn't match!! please try again")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if  request.method ==   'POST':
        user = User.query.filter_by(username= request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            flash(f'You are now logged-in as {user.username}')
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
       
    return render_template('login.html')

@login_required
@app.route('/account')
def account():
    return render_template('account.html')

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')

@login_required
@app.route('/delete', methods=['GET', 'POST'])
def delete():

    if request.method == 'POST':
        action = request.form['delete']

        post = Post.query.filter_by(id = action).first()
        print(post)
        db.session.delete(post)
        db.session.commit()
    return redirect('home')

@login_required
@app.route('/deletearchive', methods=['GET', 'POST'])
def deletearchive():
    if request.method == 'POST':
        action = request.form['delete']

        deleted_archive = Archive.query.filter_by(id = action).first()
        db.session.delete(deleted_archive)
        db.session.commit()
    return redirect('achive')

@login_required
@app.route("/achive", methods=['GET', 'POST'])
def achive():
    user = current_user.get_id()
    data = []
    archived_data = Archive.query.all()
    for make in archived_data:
        print (make)        
        data.append(make)

    if request.method  == 'POST':
        action = request.form['delete']
        action_title = request.form['add']
        action_discription = request.form['add_discription']

        post = Post.query.filter_by(id = action).first()
        db.session.delete(post)

        archives = Archive(title = action_title, discription=action_discription, archived_id = user)
        db.session.add(archives)
        db.session.commit()
        return redirect('home')
    return render_template("archive.html", context= data)
    
     