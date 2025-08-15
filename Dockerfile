FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy backend directory to app root
COPY backend/ .

# Expose port
EXPOSE 8000

# Start the application using Railway's PORT environment variable
CMD gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
