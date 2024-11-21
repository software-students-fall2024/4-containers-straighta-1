import pytest
import os
import tempfile
from .app import app, users_collection


@pytest.fixture
def client():
    """
    Creates a test client for the Flask application and sets up the environment.
    """
    app.config['TESTING'] = True

    # Use a temporary directory for uploads
    temp_upload_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = temp_upload_dir

    with app.test_client() as client:
        # Clear the MongoDB users collection for testing
        users_collection.delete_many({})
        yield client

    # Cleanup temporary directory
    for file in os.listdir(temp_upload_dir):
        os.remove(os.path.join(temp_upload_dir, file))
    os.rmdir(temp_upload_dir)


def test_home_redirect(client):
    """
    Test that the home route redirects to the login page.
    """
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_sign_up(client):
    """
    Test user sign-up functionality.
    """
    response = client.post('/sign_up', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Sign-up successful! Please log in." in response.data

    # Check if the user exists in the database
    user = users_collection.find_one({'username': 'testuser'})
    assert user is not None
    assert 'password' in user


def test_login_success(client):
    """
    Test login functionality with valid credentials.
    """
    # Add a test user
    users_collection.insert_one({
        'username': 'testuser',
        'password': app.secret_key  # Simulating pre-hashed password
    })

    response = client.post('/login', data={
        'username': 'testuser',
        'password': app.secret_key
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Login successful!" in response.data


def test_login_failure(client):
    """
    Test login functionality with invalid credentials.
    """
    response = client.post('/login', data={
        'username': 'invaliduser',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid username or password. Please try again." in response.data


def test_file_upload_success(client):
    """
    Test file upload functionality.
    """
    # Sign up and log in the user
    client.post('/sign_up', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Upload a valid file
    data = {
        'file': (tempfile.NamedTemporaryFile(delete=False, suffix='.txt'), 'testfile.txt')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b"File uploaded successfully!" in response.data


def test_file_upload_failure(client):
    """
    Test file upload functionality with invalid file type.
    """
    # Sign up and log in the user
    client.post('/sign_up', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Upload an invalid file type
    data = {
        'file': (tempfile.NamedTemporaryFile(delete=False, suffix='.exe'), 'testfile.exe')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)

    assert response.status_code == 200
    assert b"No file selected" in response.data
