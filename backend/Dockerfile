# Use a minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy all files from the current directory on the host to the container's /app directory
COPY . .

# Install Python dependencies listed in requirements.txt
RUN pip3 install -r requirements.txt

# Expose the port the Flask app will listen on
EXPOSE 7860

# Run the Flask app with gunicorn (production WSGI server) on port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "app:app"]
