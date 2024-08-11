from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_API_KEY")
MongoDBKey = os.getenv("MongoDB_API_KEY")

client = MongoClient(MongoDBKey, server_api=ServerApi('1'))
db = client[os.getenv('MongoDB_DB_NAME')]
users_collection = db[os.getenv("MongoDB_USERS")]



@app.route('/')                    
def Home():
    if 'username' in session: return render_template('Home.html')
    else: return render_template('Get_Started.html')


@app.route('/Register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        if 'username' in session: session.pop('username', None)

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if users_collection.find_one({'email': email}):
            error = "Email already exists. Please try again."
            return render_template('Register.html', error=error)

        users_collection.insert_one({'username': username, 'password': password , 'email': email})

        session['username'] = username
        return redirect(url_for('Home'))

    return render_template('Register.html')


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        if 'username' in session: session.pop('username', None)

        email = request.form.get('email')
        password = request.form.get('password')

        user = users_collection.find_one({'email': email, 'password': password})

        if user:
            session['username'] = user['username']
            return redirect(url_for('Home'))
        else:
            error = "Invalid email or password. Please try again."
            return render_template('Login.html', error=error)

    return render_template('Login.html')


@app.route('/Logout')
def Logout():
    session.pop('username', None)
    return redirect(url_for('Home'))


if __name__ == '__main__':
    app.run(debug=True)