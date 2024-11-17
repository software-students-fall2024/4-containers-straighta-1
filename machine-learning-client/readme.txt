Code related to the machine learning client goes in this folder.

ml_client have function called process_image, which will both:
    - store result data in database
    - return informations

Data will be stored in:
    database: ml_database
    collection: analysis_results

Backend must import process_image from ml_client.py
    - process_image(image_data) requires image data from upload
    - Note: ml_database will be in same cluster with database for
      uploads. 
    -   cluster: # for a mongodb cluster
            database: image_database
                collection: # for image_data
            database: ml_database
                collection: analysis_results

A possible form of data returned from process_image:

* if no image is read:
    - {"message": "Failed to decode image"}

* if no faces can be detected in image:
    - {"message": "No faces detected"}

* if successfully processed:
    - {
        "message": "Image processed",
        "results": {
            "faces_detected": 2,
            "emotions": [
                {"happy": 0.8, "neutral": 0.2},
                {"sad": 0.6, "angry": 0.4}
            ],
            "image": "data:image/png;base64,..."
        }
    }
