"""
Machine learning client to process images and detect emotions.
"""

# pylint: disable=no-member

import base64
import cv2
import numpy as np
from fer import FER
from pymongo import MongoClient

client = MongoClient("=created by teammates")
db = client["ml_database"]
collection = db["analysis_results"]

emotion_detector = FER()
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# get image from mongoDB
# might change due to backend works.
def decode_image(image_data):
    """
    Decode the image from databse
    """
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # pylint: disable=no-member
    return img


def identify_people(frame):
    """
    Identify faces in the image
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    return faces


def recognize_emotions(frame, faces):
    """
    Recognize emotions for each face.
    """
    emotions_list = []
    for x, y, w, h in faces:
        face_image = frame[y : y + h, x : x + w]
        emotions = emotion_detector.detect_emotions(face_image)
        if emotions:
            emotions_list.append(emotions[0]["emotions"])
    return emotions_list