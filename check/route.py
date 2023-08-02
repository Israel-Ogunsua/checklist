from flask.helpers import flash
from check.app import app, bcrypt
from flask import render_template,url_for,request,flash, redirect,  jsonify
import openai
from check.models import User,Post, Archive
from flask_login import login_user, login_required,current_user, logout_user
from check.models import db

# for  voice acitvation 
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
import pyttsx3

running = True

openai_api_key = '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'
openai.api_key = openai_api_key

def ask_openai(message):
    # Use the input 'message' parameter as the user's input
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},  # Use the 'message' parameter here
        ]
    )
    
    print( response)
    # Retrieve and return the assistant's response
    answer = response.choices[0].message['content'].strip()
    return answer


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.POST.get('message')
        print(message)
        response = ask_openai(message) 
        return  jsonify({'message': message, 'response': response})
    return render_template('index.html')


recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)

# talk def
def talk(text):
    engine.say(text)

# audio processing
def process_audio():

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration = 0.2)
        audio = recognizer.listen(source)

    try:
        # Perform speech recognition
        action = recognizer.recognize_google(audio)
        print("You said:", action)
        return action
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said. Please try again.")
        return None
    except sr.RequestError as e:
        print("Error occurred during recognition. Check your internet connection or API key:", e)
        return None

@app.route('/voice')
def speech():
    talk("I am your voice assistant, What can I do for you today?")
        
    while running :
        action = process_audio()
        information = "I don't have a response"
    
        if action:
            if "play" in action.lower():
                song = action.replace("play", "")
                print("Playing.....")
                information= "Playing " + song
                pywhatkit.playonyt(song)

            elif "play me" in action.lower():
                song = action.replace("play me", "")
                print("Playing.....")
                information = "Playing " + song
                pywhatkit.playonyt(song)

            elif "time" in action.lower():
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                print(current_time)
                information  = "The current time is " + current_time

            elif 'how' in action.lower():
                description = action.replace("how", "")
                information = wikipedia.summary(description, 2)
                print(information)
                talk(information)

            elif 'what' in action.lower():
                description = action.replace("how", "")
                information = wikipedia.summary(description, 2)
                print(information)
                talk(information)

            else:
                information = 'Can you say that again?'

        return render_template('speech.html', action=action, information=information)  # Pass 'action' variable to the template


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
    
     