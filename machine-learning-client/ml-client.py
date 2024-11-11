import cv2
import base64
import numpy as np
from fer import FER 
from pymongo import MongoClient

client = MongoClient("=created by teammates")
db = client["ml_database"]
collection = db["analysis_results"]

emotion_detector = FER()
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# get image from mongoDB
# might change due to backend works.
def decode_image(image_data):
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img