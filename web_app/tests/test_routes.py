import os
import io
import pytest
from app import app  # Ensure `app.py` is in the same directory as this file

# MockResponse class for mocking external API responses
class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.fixture
def client():
    """Setup a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads'  # Temporary upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.test_client() as client:
        yield client

    # Cleanup test uploads
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
        os.rmdir(app.config['UPLOAD_FOLDER'])


def test_home_redirect(client):
    """Test if the home route redirects to the login page."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location


def test_login_page(client):
    """Test if the login page renders correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_post_success(client, monkeypatch):
    """Test successful login."""
    def mock_find_one(query):
        return {'username': 'testuser', 'password': 'hashedpassword'}

    def mock_check_password_hash(hashed_password, plain_password):
        return True

    monkeypatch.setattr('pymongo.collection.Collection.find_one', mock_find_one)
    monkeypatch.setattr('werkzeug.security.check_password_hash', mock_check_password_hash)

    response = client.post('/login', data={'username': 'testuser', 'password': 'password'})
    assert response.status_code == 302
    assert '/upload' in response.location


def test_login_post_failure(client, monkeypatch):
    """Test failed login."""
    def mock_find_one(query):
        return None

    monkeypatch.setattr('pymongo.collection.Collection.find_one', mock_find_one)

    response = client.post('/login', data={'username': 'wronguser', 'password': 'password'})
    assert response.status_code == 302
    assert '/login' in response.location


def test_sign_up_page(client):
    """Test if the sign-up page renders correctly."""
    response = client.get('/sign_up')
    assert response.status_code == 200
    assert b"Sign Up" in response.data


def test_sign_up_post_success(client, monkeypatch):
    """Test successful sign-up."""
    def mock_find_one(query):
        return None

    def mock_insert_one(data):
        return None

    monkeypatch.setattr('pymongo.collection.Collection.find_one', mock_find_one)
    monkeypatch.setattr('pymongo.collection.Collection.insert_one', mock_insert_one)

    response = client.post('/sign_up', data={
        'username': 'newuser',
        'password': 'password',
        'confirm_password': 'password'
    })
    assert response.status_code == 302
    assert '/login' in response.location


def test_upload_page(client):
    """Test if the upload page renders correctly."""
    response = client.get('/upload')
    assert response.status_code == 200
    assert b"Upload" in response.data


def test_file_upload_success(client, monkeypatch):
    """Test successful file upload."""
    def mock_post(url, json):
        return MockResponse({"message": "Image processed", "results": {}}, 200)

    monkeypatch.setattr('requests.post', mock_post)

    data = {
        'file': (io.BytesIO(b"fake image data"), 'test.jpg')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data)
    assert response.status_code == 302
    assert '/analysis' in response.location


def test_analysis_page(client):
    """Test if the analysis page displays the correct results."""
    with client.session_transaction() as session:
        session['analysis'] = {
            "faces_detected": 2,
            "emotions": [{"happy": 0.8, "neutral": 0.2}, {"sad": 0.6, "angry": 0.4}]
        }

    response = client.get('/analysis?filename=test.jpg')
    assert response.status_code == 200
    assert b"Faces Detected: 2" in response.data
    assert b"happy" in response.data
    assert b"sad" in response.data
