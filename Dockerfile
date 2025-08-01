FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install MariaDB driver for Python or other dependencies that you need in 
RUN pip install mariadb

# Set working directory
WORKDIR /workspace

# Image name: pyexecutorhub-base:latest 