# pylint: disable=redefined-outer-name
"""Test module for machine learning client functionalities."""
from unittest.mock import patch, MagicMock
import base64
import pytest
import numpy as np
import cv2

from ml_client import decode_image, identify_people, recognize_emotions, process_image
from app import app


@pytest.fixture
def client():
    """Create a test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


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
    _, buffer = cv2.imencode(".jpg", sample_image)
    return base64.b64encode(buffer).decode("utf-8")


def test_sample_image_fixture(sample_image):
    """Test sample_image fixture creation."""
    assert isinstance(sample_image, np.ndarray)
    assert sample_image.shape == (100, 100, 3)


def test_encoded_image_fixture(encoded_image):
    """Test encoded_image fixture creation."""
    assert isinstance(encoded_image, str)
    decoded = base64.b64decode(encoded_image)
    assert len(decoded) > 0


@pytest.fixture
def mock_face_detector():
    """Mock the face detector to return predictable results."""
    with patch("cv2.CascadeClassifier", autospec=True) as mock_cascade:
        instance = mock_cascade.return_value
        instance.detectMultiScale.return_value = np.array([[40, 40, 20, 20]])
        return instance


@pytest.fixture
def mock_emotion_detector():
    """Mock the FER emotion detector."""
    with patch("fer.FER", autospec=True) as mock_fer:
        instance = mock_fer.return_value
        instance.detect_emotions.return_value = [
            {
                "emotions": {
                    "angry": 0.02,
                    "disgust": 0.01,
                    "fear": 0.05,
                    "happy": 0.75,
                    "sad": 0.08,
                    "surprise": 0.05,
                    "neutral": 0.04,
                }
            }
        ]
        return instance


def test_mock_face_detector_fixture(mock_face_detector):
    """Test mock_face_detector fixture returns correct values."""
    assert mock_face_detector is not None
    result = mock_face_detector.detectMultiScale(np.zeros((100, 100)))
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 4)
    assert list(result[0]) == [40, 40, 20, 20]


def test_mock_emotion_detector_fixture(mock_emotion_detector):
    """Test mock_emotion_detector fixture returns correct values."""
    assert mock_emotion_detector is not None
    result = mock_emotion_detector.detect_emotions(np.zeros((100, 100)))
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["emotions"]["happy"] == 0.75


@pytest.fixture
def mock_db_collection():
    """Mock MongoDB collection."""
    return MagicMock()


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


@patch("cv2.cvtColor")
@patch("cv2.cvtColor")
def test_identify_people(mock_cvt_color, sample_image, mock_face_detector):
    """Test face detection in an image."""
    mock_cvt_color.return_value = np.zeros((100, 100), dtype=np.uint8)
    with patch("ml_client.face_detector", mock_face_detector):
        faces = identify_people(sample_image)
        assert isinstance(faces, np.ndarray)
        assert faces.shape == (1, 4)
        assert list(faces[0]) == [40, 40, 20, 20]
        mock_face_detector.detectMultiScale.assert_called_once()


@patch("cv2.cvtColor")
def test_identify_people_no_faces(mock_cvt_color, sample_image, mock_face_detector):
    """Test face detection when no faces are present."""
    mock_cvt_color.return_value = np.zeros((100, 100), dtype=np.uint8)
    mock_face_detector.detectMultiScale.return_value = np.array([])
    with patch("ml_client.face_detector", mock_face_detector):
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


@pytest.mark.integration
@patch("cv2.cvtColor")
def test_full_pipeline_integration(
    mock_cvt_color, encoded_image, mock_face_detector, mock_emotion_detector
):
    """Test the full pipeline from image decoding to emotion recognition."""
    mock_cvt_color.return_value = np.zeros((100, 100), dtype=np.uint8)
    with patch("ml_client.face_detector", mock_face_detector), patch(
        "ml_client.emotion_detector", mock_emotion_detector
    ):
        img = decode_image(encoded_image)
        assert isinstance(img, np.ndarray)
        faces = identify_people(img)
        assert len(faces) == 1
        emotions = recognize_emotions(img, faces)
        assert len(emotions) == 1
        assert emotions[0]["happy"] == 0.75


def test_process_image_successful(encoded_image, mock_db_collection):
    """Test successful image processing workflow."""
    with patch("ml_client.decode_image") as mock_decode, patch(
        "ml_client.identify_people"
    ) as mock_identify, patch("ml_client.recognize_emotions") as mock_recognize, patch(
        "ml_client.collection", mock_db_collection
    ):

        # Setup mock returns
        mock_decode.return_value = np.zeros((100, 100, 3))
        mock_identify.return_value = np.array([[10, 20, 30, 40]])
        mock_recognize.return_value = [{"happy": 0.8, "sad": 0.2}]

        # Process image
        result = process_image(encoded_image)

        # Verify result structure and content
        assert result["message"] == "Image processed"
        assert "results" in result
        assert result["results"]["faces_detected"] == 1
        assert len(result["results"]["emotions"]) == 1
        assert result["results"]["image"] == encoded_image

        # Verify database interaction
        mock_db_collection.insert_one.assert_called_once()
