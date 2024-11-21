"""
A simple Flask web application with user authentication and file upload functionality.

The application uses Flask for handling web requests and MongoDB for storing user data. 
It provides the following features:
- User login and sign-up functionality with password hashing for security.
- File upload capability with allowed file type checks.
- A placeholder analysis route for displaying analysis results.

Modules:
    - os: For creating the upload folder if it doesn't exist.
    - flask: For handling web requests and user sessions.
    - werkzeug: For securely handling file uploads and password hashing.
    - pymongo: For connecting to and interacting with MongoDB.

Routes:
    - home: Redirects to the login page.
    - login: Handles user login and redirects to file upload page upon success.
    - sign_up: Handles user registration.
    - upload: Handles file upload functionality.
    - analysis: Displays analysis results (placeholder for future analysis functionality).

Usage:
    Run the script and navigate to the provided address in your browser to use the application.
    Make sure MongoDB is running on localhost and port 27017.
"""

import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key
"""
MongoDB setup
- Connects to a local MongoDB instance.
- Defines a database called 'user_database' and a collection called 'users'.
"""
client = MongoClient('mongodb://localhost:27017/')
db = client['user_database']
users_collection = db['users']

# File upload setup
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'csv', 'jpg', 'png', 'pdf'}

def allowed_file(filename):
    """
    Check if the file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """
    Redirect to the login page.

    Returns:
        Response: Redirect response to the login page.
    """
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    If the login is successful, redirect to the upload page.
    If the login fails, reload the login page with an error message.

    Returns:
        Response: Rendered login template or redirect response.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            flash("Login successful!", "success")
            return redirect(url_for('upload'))
        flash("Invalid username or password. Please try again.", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """
    Handle user registration.
    
    If the username already exists, reload the sign-up page with an error message.
    If the registration is successful, redirect to the login page.

    Returns:
        Response: Rendered sign-up template or redirect response.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if users_collection.find_one({'username': username}):
            flash("Username already exists. Please choose another one.", "error")
            return redirect(url_for('sign_up'))

        users_collection.insert_one({'username': username, 'password': password})
        flash("Sign-up successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('sign_up.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handle file upload.
    
    If the upload is successful, reload the upload page with a success message.
    If there is an error, reload the upload page with an error message.

    Returns:
        Response: Rendered upload template or redirect response.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part", "error")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected", "error")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("File uploaded successfully!", "success")
            return redirect(url_for('upload'))

    return render_template('upload.html')

@app.route('/analysis')
def analysis():
    """
    Display analysis results (placeholder).
    
    If no analysis results are found, redirect to the upload page with an error message.

    Returns:
        Response: Rendered analysis template or redirect response.
    """
    analysis_results = session.get('analysis', {})
    filename = request.args.get('filename', '')

    if not analysis_results:
        flash("No analysis results found. Please upload an image first.", "error")
        return redirect(url_for('upload'))

    return render_template(
        'analysis.html',
        filename=filename,
        faces=analysis_results.get('faces_detected', 0),
        emotions=analysis_results.get('emotions', [])
    )

if __name__ == '__main__':
    app.run(debug=True)
