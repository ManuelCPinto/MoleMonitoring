# Use a lightweight Python image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port 8080 for the Flask app
EXPOSE 8080

# Use Gunicorn to serve the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
