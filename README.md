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

#### *MongoDB**
No additional configuration is needed for MongoDB if running with Docker Compose.

---
## **Codebase Structure**
.
├── web-app/
│   ├── app.py                 # Flask application
│   ├── templates/             # HTML templates
│   ├── static/                # Static files (CSS, JS)
│   ├── .env                   # Environment variables
│   ├── Dockerfile             # Dockerfile for web app
│   ├── requirements.txt       # Dependencies
│   ├── tests/                 # Unit tests
├── ml-client/
│   ├── ml_client.py           # ML client code
│   ├── .env                   # Environment variables
│   ├── Dockerfile             # Dockerfile for ML client
│   ├── requirements.txt       # Dependencies
│   ├── tests/                 # Unit tests
├── docker-compose.yml         # Compose file for services
├── README.md                  # Documentation

---

## Steps necessary to run the software
1. **Install Python**:
   - Make sure Python 3.8 or higher is installed on your system. You can download it from python.org.

2. **Clone the repository**:
   - Run the following commands to create and activate the virtual environment:
     ```bash
     git clone https://github.com/software-students-fall2024/4-containers-straighta-1.git
     cd your-repository-folder
     ```
3. **Set up a Virtual Environment**:
   - Run the following commands to create and activate the virtual environment:
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows:
       ```bash
       .\venv\Scripts\activate
       ```
     - On macOS/Linux:
       ```bash
       source venv/bin/activate
       ```

4. **Install Dependencies**:
   - Use the `requirements.txt` file to install the necessary Python libraries:
     ```bash
     pip install -r requirements.txt
     ```

5. **Set up Environment Variables**:
   - Create a `.env` file in the root directory of your project and add the following variables:
    ```env
    MONGO_DBNAME=user_db
    MONGO_URI=mongodb://localhost:27017/user_db
    #MONGO_URI=mongodb+srv://zl3927:PKXFzrHguY8QDwd6@cluster0.tem8w.mongodb.net/retryWrites=true&w=majority&appName=Cluster0
    FLASK_APP=app.py
    FLASK_ENV=development
    FLASK_PORT=5000
    ```

6. **Run MongoDB (if using Docker)**
   - If you’re running MongoDB locally using Docker, start the MongoDB container:
   ```bash
   docker run --name my-mongo -d -p 27017:27017 mongo:latest
   ```
   If this code is not working, then run this: 
   ```bash
   docker-compose up --build
   ```
   - If any container has name conflicts (my-mongo):
      - stop the old containter by:
      ```bash
      docker stop my-mongo
      ```
      - After stopping, remove it with:
      ```bash
      docker rm my-mongo
      ```
      - Then start the MongoDB container.
7. **Run the Flask Application**
   - In the terminal (with the virtual environment activated), run: 
   ```bash
   python app.py
   ```
   - or using Flask if above command not working:
    ```bash
   flask run --port=5000
   ```

8. **Access the Application**
   - Open a web browser and go to `http://127.0.0.1:5000/` 
   This will take you to the login page.

9. **Deactivate the Virtual Environment (Optional)**
   - When finished, deactivate the virtual environment by typing:
     ```bas
     deactivate
     ```

10. **Contributing**
   - Fork the repository.
   - Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature
   ```
   - Commit and push your changes
   ```bash
   git commit -m "Add your feature"
   git push origin feature/your-feature
   ```
   - Open a pull request on GitHub.