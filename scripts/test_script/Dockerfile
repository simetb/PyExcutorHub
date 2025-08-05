# Test Script Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Copy the script
COPY main.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Make script executable
RUN chmod +x main.py

# Default command
CMD ["python", "main.py"] 