# pylint: disable=redefined-outer-name
"""Test module for machine learning client functionalities."""
import base64
from unittest.mock import patch
import pytest
import numpy as np
import cv2

# Import the functions to test
from ml_client import decode_image, identify_people, recognize_emotions

@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Disable pylint warning for cv2.rectangle
    # pylint: disable=no-member
    cv2.rectangle(img, (40, 40), (60, 60), (255, 255, 255), -1)
    return img

@pytest.fixture
def encoded_image(sample_image):  # pylint: disable=redefined-outer-name
    """Create a base64 encoded image for testing."""
    # Disable pylint warning for cv2.imencode
    # pylint: disable=no-member
    _, buffer = cv2.imencode('.jpg', sample_image)
    return base64.b64encode(buffer).decode('utf-8')

@pytest.fixture
def mock_face_detector():
    """Mock the face detector to return predictable results."""
    with patch('cv2.CascadeClassifier', autospec=True) as mock_cascade:
        instance = mock_cascade.return_value
        instance.detectMultiScale.return_value = np.array([[40, 40, 20, 20]])
        return instance

@pytest.fixture
def mock_emotion_detector():
    """Mock the FER emotion detector."""
    with patch('fer.FER', autospec=True) as mock_fer:
        instance = mock_fer.return_value
        instance.detect_emotions.return_value = [{
            'emotions': {
                'angry': 0.02,
                'disgust': 0.01,
                'fear': 0.05,
                'happy': 0.75,
                'sad': 0.08,
                'surprise': 0.05,
                'neutral': 0.04
            }
        }]
        return instance


def test_decode_image_valid_input(encoded_image):
    """Test decoding a valid base64 encoded image."""
    result = decode_image(encoded_image)
    assert isinstance(result, np.ndarray)
    assert len(result.shape) == 3
    assert result.shape[2] == 3

def test_decode_image_invalid_input():
    """Test decoding with invalid base64 input."""
    with pytest.raises(Exception):
        decode_image("invalid-base64-data")

@patch('cv2.cvtColor')

@patch('cv2.cvtColor')
def test_identify_people(mock_cvt_color, sample_image, mock_face_detector):
    """Test face detection in an image."""
    mock_cvt_color.return_value = np.zeros((100, 100), dtype=np.uint8)
    with patch('ml_client.face_detector', mock_face_detector):
        faces = identify_people(sample_image)
        assert isinstance(faces, np.ndarray)
        assert faces.shape == (1, 4)
        assert list(faces[0]) == [40, 40, 20, 20]
        mock_face_detector.detectMultiScale.assert_called_once()

@patch('cv2.cvtColor')
def test_identify_people_no_faces(mock_cvt_color, sample_image, mock_face_detector):
    """Test face detection when no faces are present."""
    mock_cvt_color.return_value = np.zeros((100, 100), dtype=np.uint8)
    mock_face_detector.detectMultiScale.return_value = np.array([])
    with patch('ml_client.face_detector', mock_face_detector):
        faces = identify_people(sample_image)
        assert isinstance(faces, np.ndarray)
        assert len(faces) == 0
        mock_face_detector.detectMultiScale.assert_called_once()


def test_recognize_emotions(sample_image, mock_emotion_detector):
    """Test emotion recognition for detected faces."""
    faces = np.array([[40, 40, 20, 20]])

    with patch("ml_client.emotion_detector", mock_emotion_detector):
        emotions = recognize_emotions(sample_image, faces)

        assert isinstance(emotions, list)
        assert len(emotions) == 1
        assert isinstance(emotions[0], dict)
        assert "happy" in emotions[0]
        assert emotions[0]["happy"] == 0.75


def test_recognize_emotions_no_faces(sample_image, mock_emotion_detector):
    """Test emotion recognition when no faces are provided."""
    with patch("ml_client.emotion_detector", mock_emotion_detector):
        emotions = recognize_emotions(sample_image, np.array([]))
        assert isinstance(emotions, list)
        assert len(emotions) == 0


def test_recognize_emotions_multiple_faces(sample_image, mock_emotion_detector):
    """Test emotion recognition with multiple faces."""
    faces = np.array([[40, 40, 20, 20], [70, 70, 20, 20]])

    with patch("ml_client.emotion_detector", mock_emotion_detector):
        # Configure mock to return a result for each face
        mock_emotion_detector.detect_emotions.side_effect = [
            [{"emotions": {"happy": 0.75, "sad": 0.25}}],
            [{"emotions": {"happy": 0.60, "sad": 0.40}}],
        ]

        emotions = recognize_emotions(sample_image, faces)
        assert isinstance(emotions, list)
        assert len(emotions) == 2
        assert all("happy" in emotion for emotion in emotions)


@pytest.mark.integration
@patch('cv2.cvtColor')
def test_full_pipeline_integration(mock_cvt_color, encoded_image,
                                 mock_face_detector, mock_emotion_detector):
    """Test the full pipeline from image decoding to emotion recognition."""
    mock_cvt_color.return_value = np.zeros((100, 100), dtype=np.uint8)
    with patch('ml_client.face_detector', mock_face_detector),\
         patch('ml_client.emotion_detector', mock_emotion_detector):
        img = decode_image(encoded_image)
        assert isinstance(img, np.ndarray)
        faces = identify_people(img)
        assert len(faces) == 1
        emotions = recognize_emotions(img, faces)
        assert len(emotions) == 1
        assert emotions[0]['happy'] == 0.75
