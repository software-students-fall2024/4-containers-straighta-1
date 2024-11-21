# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory's content into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5001 for the Flask app
EXPOSE 5000

# Define the command to run the Flask app
CMD ["python", "app.py"]
