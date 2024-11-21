from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['user_database']
users_collection = db['users']

# File upload setup
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'csv', 'jpg', 'png', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            flash("Login successful!", "success")
            return redirect(url_for('upload'))
        else:
            flash("Invalid username or password. Please try again.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
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

#有问题, 需要改进!!!
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
    app.run(debug=True)