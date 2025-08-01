# PyExecutorHub - The Ultimate Python Execution Platform

[![PyExecutorHub](https://img.shields.io/badge/PyExecutorHub-Platform-blue?style=for-the-badge&logo=python)](https://github.com/simetb/PyExecutorHub)

> **IMPORTANT**: This system is designed for Python scripts and bots only. Do NOT use GUI libraries like `tkinter`, `PyQt`, `wxPython`, or any graphical libraries as they will cause execution failures in the serverless environment.

## 🚀 Latest Updates (v1.0.0)

### ✨ New Features
- **Custom Docker Images**: Each script/bot can now specify its own Docker image
- **Multi-language Support**: Support for Python, Node.js, and shell scripts
- **Enhanced Log Formatting**: Improved log readability with proper line breaks
- **Flexible Execution**: Programs can use different runtime environments

### 🔧 Improvements
- **Better Error Handling**: More robust execution tracking
- **Resource Management**: Optimized memory and CPU usage
- **Documentation**: Comprehensive guides and examples

### 🐛 Bug Fixes
- **Race Condition Fix**: Resolved KeyError issues in execution tracking
- **API Hanging**: Fixed event loop blocking issues
- **Network Configuration**: Simplified Docker networking

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Custom Docker Images](#custom-docker-images)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Actions System](#actions-system)
- [Log Management](#log-management)
- [Cron Job Integration](#cron-job-integration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

PyExecutorHub is a serverless execution platform that allows you to run Python scripts and bots in isolated Docker containers. It provides a REST API for program execution, monitoring, and management.

### Key Features
- **Isolated Execution**: Each program runs in its own Docker container
- **Custom Docker Images**: Use specific images for different runtime requirements
- **Real-time Monitoring**: Track execution status and logs
- **Flexible Configuration**: Easy setup and customization
- **Actions System**: Pre and post-execution hooks
- **Multi-language Support**: Python, Node.js, and shell scripts

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
API_PORT=8000
```

## Configuration

The system uses a `config.yaml` file to define available scripts and bots. This file is mounted as a volume, allowing you to modify the configuration without rebuilding the container.

### Configuration File Structure

```yaml
scripts:
  example_script:
    id: "example_script"
    name: "Example Script"
    path: "scripts/example_script"
    description: "Example script for production"
    enabled: true
    main_file: "main.py"
    # Optional: Custom Docker image for this script
    # docker_image: "my-custom-image:latest"

  custom_image_script:
    id: "custom_image_script"
    name: "Custom Image Script"
    path: "scripts/custom_image_script"
    description: "Script using custom Docker image"
    enabled: true
    main_file: "main.py"
    docker_image: "python:3.11-slim"  # Custom image for this script

bots:
  example_bot:
    id: "example_bot"
    name: "Example Bot"
    path: "bots/example_bot"
    description: "Example bot for production"
    enabled: true
    main_file: "run.py"
    # Optional: Custom Docker image for this bot
    # docker_image: "my-custom-bot-image:latest"

  custom_image_bot:
    id: "custom_image_bot"
    name: "Custom Image Bot"
    path: "bots/custom_image_bot"
    description: "Bot using custom Docker image"
    enabled: true
    main_file: "run.py"
    docker_image: "python:3.12-slim"  # Custom image for this bot

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
curl http://localhost:8000/programs
```

#### Execute Program
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"program_id": "my_script", "parameters": {"param1": "value1"}}'
```

#### Check Execution Status
```bash
curl http://localhost:8000/executions/{execution_id}
```

### Program Structure
```
scripts/
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
- `DELETE /executions/cleanup` - Cleanup finished executions

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

## 🔧 Troubleshooting

### Common Issues

#### Program Not Found
```bash
# Check if program exists
curl http://localhost:8000/programs

# Verify configuration
cat config.yaml
```

#### Execution Failures
```bash
# Check execution status
curl http://localhost:8000/executions/{execution_id}

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
1. **Check API health**: `curl http://localhost:8000/health`
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