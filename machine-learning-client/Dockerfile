# Use Python 3.10 as specified in Pipfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock
COPY machine-learning-client/Pipfile* ./

# Install dependencies using Pipenv
# --system flag installs packages globally instead of in a virtualenv
# --deploy flag ensures packages are installed from Pipfile.lock
RUN pipenv install --system --deploy

# Install dev packages for linting and testing
RUN pipenv install --system --deploy --dev

# Copy ML client code
COPY machine-learning-client/ml_client.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0

# Run linting before starting (optional, can be removed if you prefer)
RUN pylint ml_client.py

# Command to run the ML client
CMD ["python", "ml_client.py"]