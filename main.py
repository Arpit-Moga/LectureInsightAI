from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import sqlite3 
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



@app.route('/')                     # Shows the default page based on if user is logged in or not
def Home():
    if 'username' in session: return render_template('Home.html')
    else: return render_template('Get_Started.html')


@app.route('/Register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if users_collection.find_one({'username': username}):
            return render_template('Register.html')

        users_collection.insert_one({'username': username, 'password': password , 'email': email})

        session['username'] = username
        return redirect(url_for('Home'))

    return render_template('Register.html')


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email, 'password': password})

        if user:
            session['username'] = user['username']
            return redirect(url_for('Home'))
        else:
            return render_template('Login.html')

    return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)