FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY jarvis/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY jarvis/ .

# Expose the API port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
