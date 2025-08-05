# PyExecutorHub - The Ultimate Python Execution Platform

[![PyExecutorHub](https://img.shields.io/badge/PyExecutorHub-Platform-blue?style=for-the-badge&logo=python)](https://github.com/simetb/PyExecutorHub)

> **IMPORTANT**: This system is designed for Python scripts and bots only. Do NOT use GUI libraries like `tkinter`, `PyQt`, `wxPython`, or any graphical libraries as they will cause execution failures in the serverless environment.

## 🚀 Latest Updates (v1.2.0)

### ✨ New Features
- **Test Script Included**: Simple test script to verify PyExecutorHub functionality
- **Configuration-based Image Management**: Docker images are now managed from configuration
- **Automatic Container Cleanup**: Containers are removed with `--rm` flag
- **Enhanced Validation**: Smart file detection and Docker image validation
- **Concurrent Execution Control**: Configurable limits for concurrent executions
- **Container Logs by Image**: View logs from all containers running a specific Docker image
- **Active Container Monitoring**: Real-time monitoring of all active containers
- **Enhanced Error Handling**: Better error messages and validation

### 🔧 Improvements
- **Docker Image Management**: Images are read from configuration, not system
- **Execution Limits**: Prevent system overload with concurrent execution limits
- **Better Logging**: Detailed execution logs with timing and status
- **Code Cleanup**: Removed unnecessary endpoints and methods
- **Port Configuration**: Updated to use port 8001 for consistency

### 🐛 Bug Fixes
- **Duplicate Endpoints**: Removed redundant cleanup endpoints
- **Memory Management**: Improved execution tracking and cleanup
- **Error Handling**: More specific error messages for debugging
- **File Validation**: Fixed path validation for container execution

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Custom Docker Images](#custom-docker-images)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Container Monitoring](#container-monitoring)
- [Actions System](#actions-system)
- [Log Management](#log-management)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

PyExecutorHub is a serverless execution platform that allows you to run Python scripts and bots in isolated Docker containers. It provides a REST API for program execution, monitoring, and management with advanced container monitoring capabilities.

### Key Features
- **Isolated Execution**: Each program runs in its own Docker container
- **Custom Docker Images**: Use specific images for different runtime requirements
- **Real-time Monitoring**: Track execution status and logs
- **Container Monitoring**: View logs by Docker image and active containers
- **Flexible Configuration**: Easy setup and customization
- **Actions System**: Pre and post-execution hooks
- **Multi-language Support**: Python, Node.js, and shell scripts
- **Concurrent Control**: Prevent system overload with execution limits

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client/API    │───▶│  FastAPI Server  │───▶│  Docker Engine  │
│   (HTTP/REST)   │    │  (Port 8000)     │    │  (Containers)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Program Files   │
                       │  (Scripts/Bots)  │
                       └──────────────────┘
```

## 🚀 Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/simetb/PyExecutorHub.git
cd PyExecutorHub

# Copy environment configuration
cp env.example .env

# Edit .env with your settings
nano .env

# Start the system
docker compose up -d --build
```

### Environment Configuration
Edit `.env` file:
```env
# Project configuration
HOST_PROJECT_DIR=/path/to/your/project
MAX_EXECUTIONS=50
EXECUTION_TIMEOUT=300

# Resource configuration
MEMORY_LIMIT=1g
CPU_LIMIT=0.5

# Network configuration
API_HOST=0.0.0.0
API_PORT=8001
```

## Configuration

The system uses a `config.yaml` file to define available scripts and bots. This file is mounted as a volume, allowing you to modify the configuration without rebuilding the container.

### Configuration File Structure

```yaml
scripts:
  test_script:
    id: "test_script"
    name: "Test Script"
    path: "scripts/test_script"
    description: "Simple test script to verify PyExecutorHub functionality"
    enabled: true
    main_file: "main.py"
    docker_image: "test-script:latest"  # Custom image for this script

# General system configuration
settings:
  docker_image: "pyexecutorhub-base"  # Default image for programs without custom image
  timeout_seconds: 300  # 5 minutes default
  max_concurrent_executions: 5 
  memory_limit: "1g"    # Recommended: 1GB for most cases
  cpu_limit: "0.5"      # CPU limit per container (50% of one core)
```

### Real-time Configuration Updates

The `config.yaml` file is mounted as a volume, which means:
- ✅ **No rebuild required**: Changes to the configuration file are reflected immediately
- ✅ **Live updates**: Add, modify, or remove programs without restarting the container
- ✅ **Persistent changes**: Configuration changes survive container restarts
- ✅ **Easy management**: Edit the file directly on the host system

To add a new program:
1. Edit `config.yaml` and add your program configuration
2. The new program will be available immediately via the API
3. No container restart or rebuild needed

## 🐳 Custom Docker Images

### Overview
Each script or bot can specify its own Docker image, allowing for:
- **Different runtime environments** (Python, Node.js, etc.)
- **Optimized images** for specific use cases
- **Pre-installed dependencies** for faster execution
- **Custom configurations** for different requirements

### Configuration
Add `docker_image` to your program configuration:
```yaml
my_script:
  id: "my_script"
  name: "My Script"
  path: "scripts/my_script"
  docker_image: "python:3.11-slim"  # Custom image
  main_file: "main.py"
```

### Supported Image Types

#### Python Images
```yaml
docker_image: "python:3.11-slim"
docker_image: "python:3.11-alpine"
docker_image: "python:3.12"
```

#### Node.js Images
```yaml
docker_image: "node:18-alpine"
docker_image: "node:20-slim"
docker_image: "node:latest"
```

#### Other Images
```yaml
docker_image: "ubuntu:22.04"
docker_image: "debian:bullseye-slim"
docker_image: "alpine:latest"
```

### Image Requirements
- **Must support shell commands** (bash/sh)
- **Should have the required runtime** (python, node, etc.)
- **Must be available locally** or pullable from Docker Hub
- **Should be optimized** for your use case

### Examples

#### Python Script with Custom Image
```python
#!/usr/bin/env python3
import os
import sys

def main():
    print(f"Python version: {sys.version}")
    print(f"Running in container: {os.path.exists('/.dockerenv')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

#### Node.js Bot with Custom Image
```javascript
#!/usr/bin/env node
const os = require('os');

function main() {
    console.log(`Node.js version: ${process.version}`);
    console.log(`Platform: ${process.platform}`);
    process.exit(0);
}

main();
```

### Best Practices
1. **Use specific versions** instead of `latest`
2. **Choose lightweight images** when possible
3. **Test your images** before production
4. **Document image requirements** in your code
5. **Use multi-stage builds** for complex setups

## 📖 Usage

### API Endpoints

#### List Programs
```bash
curl http://localhost:8001/programs
```

#### Execute Program
```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"program_id": "test_script", "parameters": {"param1": "value1"}}'
```

#### Check Execution Status
```bash
curl http://localhost:8001/executions/{execution_id}
```

#### Test Script Example
```bash
# Execute the test script
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"program_id": "test_script"}'

# Check status
curl http://localhost:8001/executions/{execution_id}

# Get detailed logs
curl http://localhost:8001/executions/{execution_id}/logs
```

### Program Structure
```
scripts/
├── test_script/         # Test script (included)
│   ├── main.py          # Main script file
│   ├── Dockerfile       # Docker image definition
│   ├── .env             # Environment variables
│   └── env.example      # Environment variables template
├── my_script/
│   ├── main.py          # Main script file
│   ├── requirements.txt  # Python dependencies
│   └── env.example      # Environment variables template

bots/
├── my_bot/
│   ├── run.py           # Main bot file
│   ├── requirements.txt  # Python dependencies
│   └── env.example      # Environment variables template
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /programs` - List all programs
- `POST /execute` - Execute a program
- `GET /executions` - List all executions
- `GET /executions/{id}` - Get execution status

### Management Endpoints
- `GET /executions/info` - Execution statistics
- `GET /executions/stats` - Detailed statistics
- `GET /executions/concurrent` - Concurrent execution information
- `DELETE /executions/cleanup` - Cleanup finished executions

### Container Monitoring Endpoints
- `GET /containers/logs/{image_name}` - Get logs from containers by Docker image
- `GET /containers/active` - Get all active containers
- `GET /executions/{execution_id}/logs` - Get detailed execution logs with timing

### Docker Images Endpoints
- `GET /images/available` - Get all available Docker images from configuration
- `GET /images/search/{image_name}` - Search for specific Docker images in configuration

## 🧪 Test Script

### Overview
A simple test script is included to verify PyExecutorHub functionality:

**Location**: `scripts/test_script/`
**Image**: `test-script:latest`
**Main File**: `main.py`

### Quick Test
```bash
# Build the test image
cd scripts/test_script && docker build -t test-script:latest .

# Test manually
docker run --rm -e MY_NAME=Temis test-script:latest

# Test with PyExecutorHub
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"program_id": "test_script"}'
```

### Expected Output
```
==================================================
🚀 PyExecutorHub Test Script
==================================================
⏰ Execution Time: 2025-08-05 09:52:10
📋 Program ID: test_script
🆔 Execution ID: 0e14651b-9ed4-43f7-a5db-f6f5e917fb66
👋 Hola mundo Temis!
==================================================
🐳 Running inside Docker container
🐍 Python version: 3.11.13
📝 No custom parameters provided
==================================================
✅ Test script completed successfully!
==================================================
```

## 🐳 Container Monitoring

### Overview
Advanced container monitoring capabilities allow you to track and debug running containers by Docker image and get real-time logs.

### Container Logs by Image
View logs from all containers running a specific Docker image:

```bash
# Get logs from all containers using python:3.11-slim
curl http://localhost:8001/containers/logs/python:3.11-slim

# Response
{
  "image_name": "python:3.11-slim",
  "containers": [
    {
      "container_id": "abc123def456",
      "stdout": "Program output...",
      "stderr": "",
      "logs_lines": 15
    }
  ],
  "total_containers": 1,
  "message": "Found 1 running containers for image: python:3.11-slim"
}
```

### Active Containers
Monitor all currently running containers:

```bash
# Get all active containers
curl http://localhost:8001/containers/active

# Response
{
  "total_containers": 3,
  "containers": [
    {
      "container_id": "abc123def456",
      "image": "python:3.11-slim",
      "status": "Up 2 minutes",
      "name": "friendly_container_name"
    },
    {
      "container_id": "def456ghi789",
      "image": "node:18-alpine",
      "status": "Up 1 minute",
      "name": "node_container"
    }
  ]
}
```

### Concurrent Execution Monitoring
Track concurrent executions and prevent system overload:

```bash
# Get concurrent execution information
curl http://localhost:8001/executions/concurrent

# Response
{
  "concurrent_count": 2,
  "max_concurrent": 5,
  "running_executions": [
    {
      "execution_id": "uuid-1",
      "program_id": "my_script",
      "start_time": "2024-01-01T10:00:00",
      "duration_seconds": 45.2
    }
  ]
}
```

### Enhanced Execution Logs
Get detailed execution information with timing:

```bash
# Get detailed execution logs
curl http://localhost:8001/executions/{execution_id}/logs

# Response
{
  "execution_id": "uuid-1",
  "program_id": "my_script",
  "status": "completed",
  "start_time": "2024-01-01T10:00:00",
  "end_time": "2024-01-01T10:00:45",
  "duration_seconds": 45.2,
  "output": "Program output...",
  "error": "",
  "output_lines": 10,
  "error_lines": 0
}
```

## 🐳 Docker Images Management

### Overview
Manage and monitor Docker images used by the system. Get information about available images from the configuration and search for specific ones.

### Available Images
Get all Docker images configured in the system:

```bash
# Get all available images from configuration
curl http://localhost:8001/images/available

# Response
{
  "total_images": 2,
  "images": [
    {
      "repository": "test-script",
      "tag": "latest",
      "image_id": "config",
      "size": "N/A",
      "created_at": "N/A",
      "full_name": "test-script:latest",
      "source": "script",
      "script_id": "test_script"
    },
    {
      "repository": "pyexecutorhub-base",
      "tag": "latest",
      "image_id": "config",
      "size": "N/A",
      "created_at": "N/A",
      "full_name": "pyexecutorhub-base",
      "source": "default",
      "description": "Default image for programs without custom image"
    }
  ]
}
```

### Search Images
Search for specific Docker images in configuration:

```bash
# Search for test-script images
curl http://localhost:8001/images/search/test-script

# Response
{
  "search_term": "test-script",
  "total_images": 1,
  "images": [
    {
      "repository": "test-script",
      "tag": "latest",
      "image_id": "config",
      "size": "N/A",
      "created_at": "N/A",
      "full_name": "test-script:latest",
      "source": "script",
      "script_id": "test_script"
    }
  ]
}
```

### Container Cleanup
The system automatically removes containers after execution using the `--rm` flag:

- ✅ **Automatic cleanup**: Containers are removed after execution
- ✅ **No accumulation**: Prevents container buildup
- ✅ **Resource management**: Frees up system resources
- ✅ **Clean environment**: Each execution starts fresh

### Image Management Best Practices

#### 1. **Use Specific Tags**
```yaml
# Good - Specific version
docker_image: "python:3.11-slim"

# Avoid - Latest tag
docker_image: "python:latest"
```

#### 2. **Regular Cleanup**
```bash
# Remove unused images
docker image prune -f

# Remove all unused images (including untagged)
docker image prune -a -f
```

#### 3. **Monitor Image Usage**
```bash
# Check image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Find large images
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -hr
```

## ⚡ Actions System

### Overview
Actions are Python scripts that run before and after program execution, providing hooks for:
- **Pre-execution setup** (database connections, file preparation)
- **Post-execution cleanup** (log processing, notifications)
- **Custom workflows** (data validation, reporting)

### Structure
```
actions/
├── act_before.py        # Pre-execution actions
├── act_after.py         # Post-execution actions
├── requirements.txt     # Action dependencies
└── README.md           # Documentation
```

### Environment Variables
Actions have access to:
- `PROGRAM_ID` - Current program ID
- `EXECUTION_ID` - Current execution ID
- `EXIT_CODE` - Program exit code (post-execution only)
- All custom parameters as `PARAM_*` variables

### Example Actions
```python
# act_before.py
import os
import logging

def main():
    program_id = os.getenv('PROGRAM_ID')
    execution_id = os.getenv('EXECUTION_ID')
    
    logging.info(f"Starting execution {execution_id} for program {program_id}")
    
    # Your pre-execution logic here
    print("🔧 Pre-execution actions completed")

if __name__ == "__main__":
    main()
```

```python
# act_after.py
import os
import requests

def main():
    exit_code = os.getenv('EXIT_CODE', '0')
    program_id = os.getenv('PROGRAM_ID')
    
    if exit_code == '0':
        print("✅ Program completed successfully")
        # Send success notification
    else:
        print(f"❌ Program failed with exit code {exit_code}")
        # Send failure notification

if __name__ == "__main__":
    main()
```

## 📊 Log Management

### Enhanced Log Formatting
Logs are automatically formatted for better readability:
- **Line breaks** are properly displayed
- **Escape sequences** are handled correctly
- **Output and error** streams are separated

### Viewing Logs
```bash
# Get execution status with logs
curl http://localhost:8000/executions/{execution_id}

# Example response
{
  "execution_id": "abc123",
  "program_id": "my_script",
  "status": "completed",
  "output": "Program started\nProcessing data...\nCompleted successfully",
  "error": ""
}
```

### Log Levels
- **INFO**: General execution information
- **WARNING**: Non-critical issues
- **ERROR**: Execution failures
- **DEBUG**: Detailed debugging information

## ⏰ Cron Job Integration

### Automated Execution
Set up cron jobs for automated program execution:

```bash
# Execute bot every 8 hours
0 */8 * * * /path/to/execute_bot.sh 6
```

### Execution Script (`execute_bot.sh`)
```bash
#!/bin/bash
PROGRAM_ID=$1

if [ -z "$PROGRAM_ID" ]; then
    echo "Usage: $0 <program_id>"
    exit 1
fi

curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d "{\"program_id\": \"$PROGRAM_ID\"}" \
  -s > /dev/null

echo "Bot $PROGRAM_ID execution triggered at $(date)"
```

### Server Migration
When migrating to a new server:
```bash
# Update cron jobs
crontab -e

# Change paths from old system to new
# Old: /apps/serverless-executor/execute_bot.sh
# New: /apps/PyExecutorHub/execute_bot.sh
```

## 🛡️ Validation & Error Handling

### Docker Image Validation
The system automatically validates and manages Docker images:

#### Image Not Found
```bash
# Error when image doesn't exist
❌ Docker image 'python:3.11-slim' not found and could not be pulled. 
Please ensure the image exists locally or is available in a registry.
```

#### Automatic Image Pull
- ✅ **Local Check**: First verifies if image exists locally
- ✅ **Auto Pull**: Attempts to download from Docker Hub if not found
- ✅ **Timeout**: 5-minute timeout for image downloads
- ✅ **Error Handling**: Clear error messages with instructions

### File Validation
Smart detection of main program files:

#### Supported File Types
- `main.py` (default)
- `run.py` (alternative)
- `app.py` (alternative)
- `index.py` (alternative)

#### File Not Found Error
```bash
# Error when main file is missing
❌ Main program file 'main.py' not found in /path/to/scripts/mi_script. 
Please ensure the file exists or update the configuration.
```

### Concurrent Execution Control
Prevents system overload with configurable limits:

#### Configuration
```yaml
settings:
  max_concurrent_executions: 5  # Maximum concurrent executions
```

#### Limit Exceeded Error
```bash
# Error when concurrent limit is reached
❌ Maximum concurrent executions (5) reached. 
Please wait for some executions to complete.
```

### Error Categories

#### 1. **Image Errors**
- Image not found locally
- Failed to pull from registry
- Invalid image name

#### 2. **File Errors**
- Main file not found
- Invalid file path
- Missing dependencies

#### 3. **Execution Errors**
- Concurrent limit exceeded
- Timeout exceeded
- Resource limits reached

#### 4. **System Errors**
- Docker daemon not available
- Insufficient permissions
- Network connectivity issues

### Debugging Validation Issues

#### Check Image Availability
```bash
# List local images
docker images

# Check specific image
docker images python:3.11-slim

# Pull image manually
docker pull python:3.11-slim
```

#### Verify File Structure
```bash
# Check program directory
ls -la scripts/mi_script/

# Verify main file exists
ls -la scripts/mi_script/main.py

# Check alternative files
ls -la scripts/mi_script/run.py
```

#### Monitor Concurrent Executions
```bash
# Check current concurrent executions
curl http://localhost:8000/executions/concurrent

# View all executions
curl http://localhost:8000/executions
```

## 🔧 Troubleshooting

### Common Issues

#### Program Not Found
```bash
# Check if program exists
curl http://localhost:8001/programs

# Verify configuration
cat config.yaml
```

#### Execution Failures
```bash
# Check execution status
curl http://localhost:8001/executions/{execution_id}

# View container logs
docker logs pyexecutorhub-api
```

#### Docker Image Issues
```bash
# Check available images
docker images

# Pull missing images
docker pull python:3.11-slim
```

### Debugging Steps
1. **Check API health**: `curl http://localhost:8001/health`
2. **Verify configuration**: Review `config.yaml`
3. **Check Docker**: `docker ps -a`
4. **View logs**: `docker logs pyexecutorhub-api`
5. **Test manually**: Run program directly in container

### Performance Optimization
- **Use lightweight images** (alpine, slim)
- **Optimize dependencies** (only required packages)
- **Set appropriate timeouts** for your use case
- **Monitor resource usage** regularly

## 📚 Examples

### Test Script (Included)
```python
#!/usr/bin/env python3
"""
Test Script for PyExecutorHub
Simple script to test environment variables and Docker execution
"""

import os
import sys
from datetime import datetime

def main():
    """Main function that reads environment variables and displays a message"""
    
    # Get environment variables
    program_id = os.getenv('PROGRAM_ID', 'unknown')
    execution_id = os.getenv('EXECUTION_ID', 'unknown')
    my_name = os.getenv('MY_NAME', 'World')
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 50)
    print("🚀 PyExecutorHub Test Script")
    print("=" * 50)
    print(f"⏰ Execution Time: {current_time}")
    print(f"📋 Program ID: {program_id}")
    print(f"🆔 Execution ID: {execution_id}")
    print(f"👋 Hola mundo {my_name}!")
    print("=" * 50)
    
    # Check if running in Docker
    if os.path.exists('/.dockerenv'):
        print("🐳 Running inside Docker container")
    else:
        print("💻 Running on host system")
    
    # Display Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if we have any parameters
    param_count = 0
    for key, value in os.environ.items():
        if key.startswith('PARAM_'):
            param_count += 1
            print(f"📝 Parameter {key}: {value}")
    
    if param_count == 0:
        print("📝 No custom parameters provided")
    
    print("=" * 50)
    print("✅ Test script completed successfully!")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Basic Python Script
```python
#!/usr/bin/env python3
import os
import sys

def main():
    print("Hello from PyExecutorHub!")
    print(f"Program ID: {os.getenv('PROGRAM_ID')}")
    print(f"Execution ID: {os.getenv('EXECUTION_ID')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Script with Parameters
```python
#!/usr/bin/env python3
import os
import sys

def main():
    # Access custom parameters
    param1 = os.getenv('PARAM_PARAM1', 'default')
    param2 = os.getenv('PARAM_PARAM2', 'default')
    
    print(f"Parameter 1: {param1}")
    print(f"Parameter 2: {param2}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Bot with Database Connection
```python
#!/usr/bin/env python3
import os
import sys
import mariadb

def main():
    try:
        # Connect to database
        conn = mariadb.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        
        # Your bot logic here
        print("Bot executed successfully")
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- **Documentation**: Check this README and the [actions README](actions/README.md)
- **Issues**: Report bugs and feature requests on GitHub
- **Examples**: Review the example scripts and bots in the repository

---

**PyExecutorHub** - Making Python execution simple, scalable, and reliable! 🚀 