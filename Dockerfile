
# Use a lightweight Python base image
FROM python:3.11-slim

# Install system dependencies (Tesseract + build tools)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Command to run Flask (or use Gunicorn for production)
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000"]