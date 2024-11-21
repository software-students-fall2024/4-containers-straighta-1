import sys
import os
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
sys.path.append(os.path.abspath('../mlc'))

from ml_client import process_image
 # Import process_image from ml_client.py

# Load environment variables
load_dotenv()

def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

    # MongoDB setup
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db = client['user_database']
    users_collection = db['users']

    # Test MongoDB connection
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

    # Routes
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
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash("Passwords do not match!", "error")
                return redirect(url_for('sign_up'))

            if users_collection.find_one({'username': username}):
                flash("Username already exists. Please choose another one.", "error")
                return redirect(url_for('sign_up'))

            hashed_password = generate_password_hash(password)
            users_collection.insert_one({'username': username, 'password': hashed_password})
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
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Call the ML client to process the image
                try:
                    with open(filepath, 'rb') as image_file:
                        image_data = base64.b64encode(image_file.read())
                        analysis_results = process_image(image_data)

                    if analysis_results['message'] != "Image processed":
                        flash(analysis_results['message'], "error")
                        return redirect(url_for('upload'))

                    # Store results in session and redirect to /analysis
                    session['analysis'] = analysis_results['results']
                    return redirect(url_for('analysis', filename=filename))

                except Exception as e:
                    flash(f"Error processing image: {e}", "error")
                    return redirect(url_for('upload'))

        return render_template('upload.html')

    @app.route('/analysis')
    def analysis():
        """Display analysis results."""
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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)