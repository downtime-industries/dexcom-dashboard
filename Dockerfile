FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py ./

# Expose Prometheus metrics port
EXPOSE 8000

# Define entrypoint
CMD ["python", "main.py"]
