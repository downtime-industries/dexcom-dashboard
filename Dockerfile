FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose log directory and set environment variables
ENV LOG_DIR=/var/log/dexcom
RUN mkdir -p $LOG_DIR

# Define entrypoint
CMD ["python", "main.py"]
