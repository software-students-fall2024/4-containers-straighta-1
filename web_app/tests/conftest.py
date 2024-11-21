import pytest
from web_app.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = 'tests/uploads'
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client
