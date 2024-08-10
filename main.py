from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import sqlite3 
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_API_KEY")
MongoDBKey = os.getenv("MongoDB_API_KEY")

client = MongoClient(MongoDBKey, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# def get_db_connection():
#     conn = sqlite3.connect('Database/database.db')
#     conn.row_factory = sqlite3.Row
#     return conn


# @app.route('/')                     # Shows the default page based on if user is logged in or not
# def Home():
#     if 'username' in session: return render_template('Home.html',username = session['username'])
#     else: return render_template('Get_Started.html')


# @app.route('/Register', methods=('GET', 'POST'))
# def Register():
#     if request.method == 'POST':

#         username = request.form['username']
#         password = request.form['password']

#         conn = get_db_connection()
#         cur = conn.cursor()

#         cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
#         conn.commit()
#         conn.close()

#         session['username'] = username
#         return redirect(url_for('Home',username=username))
    
#     return render_template('Register.html')


# @app.route('/Login', methods=('GET', 'POST'))
# def Login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         conn = get_db_connection()
#         cur = conn.cursor()

#         cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
#         user = cur.fetchone()
#         conn.close()

#         if user:
#             session['username'] = username
#             return redirect(url_for('Home',username=username))

#     return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)