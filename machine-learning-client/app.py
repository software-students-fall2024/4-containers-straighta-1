"""
Flask application to provide an API for processing images
via the ml-client module.
"""

from flask import Flask, request, jsonify
from ml_client import process_image

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process_image_api():
    """
    API to process the image and return analysis results.
    """
    data = request.get_json()
    image_data = data.get("image")

    if not image_data:
        return jsonify({"message": "No image data provided"}), 400

    result = process_image(image_data)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
