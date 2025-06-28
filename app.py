from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from flask import flash

load_dotenv()


app = Flask(__name__)
app.secret_key = 'nutrisync_secret_key'

# MongoDB config — replace "nutrisyncDB" if you want a different DB name
app.config["MONGO_URI"] = "mongodb://localhost:27017/nutrisyncDB"
mongo = PyMongo(app)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = {
            "name": request.form['name'],
            "gender": request.form['gender'],
            "dob": request.form['dob'],
            "height": request.form['height'],
            "weight": request.form['weight'],
            "goal_weight": request.form['goal_weight'],
            "phone": request.form.get('phone'),  # Optional field
            "username": request.form['username'],
            "password": request.form['password'],
            "fitness_goal": request.form['fitness_goal'],
            "activity_level": request.form['activity_level']
        }

        # Check if username already exists
        existing_user = mongo.db.users.find_one({'username': user['username']})
        if existing_user:
            return "Username already exists. Please try another."

        mongo.db.users.insert_one(user)
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# User Profile
@app.route('/user')
def user_profile():
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})
        updated = request.args.get('updated', 'false')
        return render_template('user.html', user=user)
    else:
        return redirect(url_for('login'))

# Update User Info
@app.route('/update_user', methods=['POST'])
def update_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    updated_data = {
        'age': request.form['age'],
        'height': request.form['height'],
        'weight': request.form['weight']
    }

    mongo.db.users.update_one(
        {'username': username},
        {'$set': updated_data}
    )

    return redirect(url_for('user_profile',updated='true'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})


        health_logs = user.get('health_logs', [])
        health_logs.sort(key=lambda log: datetime.strptime(log['date'], '%Y-%m-%d'))
        return render_template('dashboard.html', user=user, health_logs=health_logs)

    else:
        return redirect(url_for('login'))

# logging health data

@app.route('/log', methods=['POST'])
def log_daily_data():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    date = request.form['date']
    weight = float(request.form.get('weight', 0))
    water = float(request.form.get('water', 0))
    sleep = float(request.form.get('sleep', 0))

    log_entry = {
        "date": date,
        "weight": weight,
        "water_intake": water,
        "sleep_hours": sleep
    }

    mongo.db.users.update_one(
        {"username": username},
        {"$push": {"health_logs": log_entry}}
    )

    flash("Health data logged successfully!")
    return redirect(url_for('dashboard'))

# chatbot route

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_message = request.form.get('message')
    bot_reply = ""

    headers = {
        "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)

    try:
        bot_reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Groq API Error:", response.text)
        bot_reply = "⚠️ Error getting response from the chatbot."

    user = mongo.db.users.find_one({'username': session['username']})
    health_logs = user.get('health_logs', [])
    health_logs.sort(key=lambda log: datetime.strptime(log['date'], '%Y-%m-%d'))

    return render_template("dashboard.html", user=user, health_logs=health_logs, user_message=user_message, bot_reply=bot_reply)

# dashboard profile edit
@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Build the updated data dictionary using form values
    updated_data = {
        "name": request.form['name'],
        "gender": request.form['gender'],
        "dob": request.form['dob'],
        "height": request.form['height'],
        "weight": request.form['weight'],
        "goal_weight": request.form['goal_weight'],
        "phone": request.form.get('phone', ''),
        "username": request.form['username'],
        "fitness_goal": request.form['fitness_goal'],
        "activity_level": request.form['activity_level']
    }

    # Only update password if the user provided a new value
    new_password = request.form.get('password', '')
    if new_password:
        updated_data["password"] = new_password  # For production, hash the password

    # Update the user's record in MongoDB
    mongo.db.users.update_one(
        {"username": username},
        {"$set": updated_data}
    )

    flash("Profile updated successfully!")
    return redirect(url_for('dashboard'))
# dietfitness page
@app.route('/dietfitness')
def diet_fitness():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dietfitness.html')

# Logout (optional)
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
