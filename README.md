![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

# Containerized App Exercise

# Project Name: Emotion Detection System

## **Project Description**
This project is an **Emotion Detection System** built using Python, Flask, and MongoDB. It consists of two main subsystems:
1. **Web App**:
   - Built with Flask, it allows users to upload images and view analysis results.
   - Connects to MongoDB for storing and retrieving data.
2. **Machine Learning Client**:
   - Processes images to detect faces and emotions.
   - Saves analysis results to MongoDB.
3. **MongoDB**:
   - Acts as the database for storing uploaded images and analysis results.

Key Features:
- Face detection and emotion analysis.
- Real-time dashboard displaying results.
- Seamless integration with MongoDB for data storage.
- Built-in CI/CD workflows for testing and code quality checks.

---

## **Team Members**
- [Elaine Lyu](https://github.com/ElaineR02)
- [Linda Li](https://github.com/Applejam-ovo)
- [Rita He]( https://github.com/ritaziruihe)
- [Hannah Liang](https://github.com/HannahLiang627)

---

## **Subsystems**

### **1. Web App**
- **Technology**: Python (Flask).
- **Functionality**:
  - Allows users to upload images.
  - Displays analysis results from MongoDB.
- **Code Location**: `web-app/`.

### **2. Machine Learning Client**
- **Technology**: Python.
- **Functionality**:
  - Processes images for facial detection and emotion analysis.
  - Saves analysis results to MongoDB.
- **Code Location**: `ml-client/`.

### **3. MongoDB**
- **Technology**: MongoDB database.
- **Functionality**:
  - Stores image data and analysis results.
  - Used by both Web App and ML Client subsystems.
- **Setup**: Runs in a Docker container.

---

## **Setup and Configuration**

### **System Requirements**
- Python 3.10 or higher
- Docker and Docker Compose
- MongoDB (local or Atlas cluster)

### **Environment Variables**
Create a `.env` file in both the `web-app/` and `ml-client/` directories. Include the following variables:

#### **Web App `.env`**
```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://mongo:27017/
```

#### **ML Client `.env`**

MONGO_URI=mongodb://mongo:27017/
DATABASE_NAME=ml_database
COLLECTION_NAME=analysis_results