FROM python:3.11-slim

# Install system dependencies including LibreOffice
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-draw \
    libreoffice-math \
    libreoffice-base \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN pip install --upgrade pip

# Install MariaDB driver for Python or other dependencies that you need in 
RUN pip install mariadb

# Set working directory
WORKDIR /workspace

# Image name: pyexecutorhub-base:latest 