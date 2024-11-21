import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Change this to a strong secret key

    # MongoDB setup
    client = MongoClient('mongodb://localhost:27017/')
    db = client['user_database']
    users_collection = db['users']

    try:
        client.admin.command("ping")
        print(" * Connected to MongoDB!")
    except ConnectionFailure as e:
        print(" * MongoDB connection error:", e)

    # File upload setup
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    allowed_extensions = {'txt', 'csv', 'jpg', 'png', 'pdf'}

    def allowed_file(filename):
        """Check if the file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @app.route('/')
    def home():
        """Redirect to the login page."""
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login."""
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
        """Handle user sign-up."""
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
        """Handle file uploads."""
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

    if __name__ == '__main__':
        app.run(debug=True)