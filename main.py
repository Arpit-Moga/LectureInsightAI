from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from bson import ObjectId
from gridfs import GridFS
import os
import ai_helper_script



load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_API_KEY")
MongoDBKey = os.getenv("MongoDB_API_KEY")

client = MongoClient(MongoDBKey, server_api=ServerApi('1'))
db = client[os.getenv('MongoDB_DB_NAME')]
users_collection = db[os.getenv("MongoDB_USERS")]
fs = GridFS(db)



@app.route('/')
def Home():
    if 'username' in session: return render_template('Home.html')
    else: return render_template('Get_Started.html')

@app.route('/Login', methods=('GET', 'POST'))
def Login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('Home'))
        else:
            return render_template('Login.html', error='Invalid email or password')

    return render_template('Login.html')

@app.route('/Register', methods=('GET', 'POST'))
def Register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'courses': []
        })

        session['username'] = username
        return redirect(url_for('Home'))

    return render_template('Register.html')

@app.route('/Logout')
def Logout():
    session.pop('username', None)
    return redirect(url_for('Home'))


                                                                            
@app.route('/Upload', methods=['POST'])
def Upload():
    if 'username' not in session:
        return redirect(url_for('Login'))

    username = session['username']
    if 'file' not in request.files: return redirect(request.url)

    file = request.files['file']
    
    if file.filename == '': return redirect(request.url)

    if file and allowed_file(file.filename):
        file_id = fs.put(file, filename=file.filename, user=username)
        users_collection.update_one(
            {'username': username},
            {'$addToSet': {'courses': {'filename': file.filename, 'file_id': file_id}}}
        )
    return redirect(url_for('view_course', course_id=file_id))

@app.route('/Course/<course_id>', methods=['GET','POST'])
def view_course(course_id):
    if 'username' not in session: return render_template('Get_Started.html')

    username = session['username']
    user = users_collection.find_one({'username': username})
    
    if user:
        if not ObjectId.is_valid(course_id): return jsonify({'error': 'Invalid course ID'}), 400
        
        course = users_collection.find_one({'username': username, 'courses.file_id': ObjectId(course_id)})
        if not course: return jsonify({'error': 'Course not found or access denied'}), 404

        course_data = next(c for c in course['courses'] if c['file_id'] == ObjectId(course_id))
        note = users_collection.find_one({'username': username, 'courses.file_id': ObjectId(course_id)}, {'courses.$': 1})
        summary = note['courses'][0].get('note', None) if note else None
        key_points = note['courses'][0].get('key_points', None) if note else None

        if request.method == 'POST' and 'generate_note' in request.form: 
            summary = ai_helper_script.AI_summary(fs,course_data)
            key_points = ai_helper_script.AI_key_points(summary)

        users_collection.update_one(
            {'username': username, 'courses.file_id': ObjectId(course_id)},
                {
                    '$set': {
                        'courses.$.note': summary,
                        'courses.$.key_points': key_points
                    }
                }
        )

        print(key_points)

        return render_template('Course_Detail.html', course=course_data , summary=summary , key_points=key_points)
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/courses', methods=['GET'])
def get_courses():
    if 'username' not in session: return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']
    user = users_collection.find_one({'username': username})

    if user:
        courses = user.get('courses', [])
        for course in courses:
            if isinstance(course.get('file_id'), ObjectId): course['file_id'] = str(course['file_id'])
        return jsonify({'courses': courses})
    
    else: return jsonify({'error': 'User not found'}), 404

def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}



if __name__ == '__main__':
    app.run(debug=True)