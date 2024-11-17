# Test stage with coverage reporting
FROM python:3.10-slim as test
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pipenv
COPY machine-learning-client/Pipfile* ./
RUN pipenv install --system --deploy --dev
COPY machine-learning-client/ml_client.py ./
COPY machine-learning-client/test_ml_client.py ./
RUN pylint ml_client.py test_ml_client.py && \
    coverage report -m machine-learning-client/test_ml_client.py machine-learning-client/ml_client.py

# Production stage
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pipenv
COPY machine-learning-client/Pipfile* ./
RUN pipenv install --system --deploy
COPY machine-learning-client/ml_client.py ./
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0
CMD ["python", "ml_cli