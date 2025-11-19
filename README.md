# PyExecutorHub - The Ultimate Python Execution Platform

[![PyExecutorHub](https://img.shields.io/badge/PyExecutorHub-Platform-blue?style=for-the-badge&logo=python)](https://github.com/simetb/PyExecutorHub)

> **IMPORTANT**: This system is designed for Python scripts and bots only. Do NOT use GUI libraries like `tkinter`, `PyQt`, `wxPython`, or any graphical libraries as they will cause execution failures in the serverless environment.

## 🚀 Latest Updates (v1.4.0)

### ✨ New Features
- **🏗️ Modular Architecture**: Complete codebase refactoring with separated routes, services, models, and utilities
- **📦 Distributed Structure**: Code organized by endpoints for better maintainability and scalability
- **🔐 Secure Authentication System**: JWT-based authentication with random credentials generated at startup
- **📋 Parameterized Program Execution**: Configure command-line parameters for each program
- **📊 Enhanced Statistics**: Detailed execution breakdown by status and program name
- **🐳 LibreOffice Integration**: Base image now includes LibreOffice suite for document processing
- **📁 External Scripts Support**: Mount external directories as volumes for scripts/bots outside the project
- **🔧 Improved Base Image**: Upgraded pip and added comprehensive LibreOffice packages
- **📝 Better Logging**: Enhanced parameter logging and execution tracking
- **🛡️ Endpoint Protection**: All API endpoints now require authentication

### 🔧 Improvements
- **Code Organization**: Separated concerns into routes/, services/, models/, and utils/ directories
- **Maintainability**: Each endpoint has its own route file for easier maintenance
- **Scalability**: Easy to add new endpoints and services without modifying core files
- **Configuration Management**: Added parameters field to program configuration
- **Multi-language Parameter Support**: Parameters work with Python, Node.js, and Shell scripts
- **Security Enhancement**: Credentials shown only once at startup for security
- **Resource Optimization**: Updated CPU limits and memory configuration
- **Error Handling**: Better validation and error messages for parameters
- **Documentation**: Comprehensive examples and usage guides

### 🐛 Bug Fixes
- **Port Consistency**: Fixed port configuration across all files (8001)
- **Service Name Alignment**: Corrected service names in scripts and documentation
- **Path Configuration**: Fixed hardcoded paths and environment variable usage
- **Resource Limits**: Aligned CPU limits between configuration and Docker Compose
- **Authentication Flow**: Streamlined login process and token management

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Authentication](#authentication)
- [Configuration](#configuration)
  - [Configuration Options](#configuration-options)
  - [Docker Compose Execution](#docker-compose-execution)
  - [External Scripts and Bots (Volume Mounting)](#external-scripts-and-bots-volume-mounting)
  - [Real-time Configuration Updates](#real-time-configuration-updates)
- [Parameterized Execution](#parameterized-execution)
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
- **🔐 Secure Authentication**: JWT-based authentication with random credentials
- **📋 Parameterized Execution**: Configure command-line parameters for each program
- **🏗️ Isolated Execution**: Each program runs in its own Docker container
- **🐳 Custom Docker Images**: Use specific images for different runtime requirements
- **📊 Real-time Monitoring**: Track execution status and detailed statistics
- **🔍 Container Monitoring**: View logs by Docker image and active containers
- **⚙️ Flexible Configuration**: Easy setup and customization
- **🔧 Actions System**: Pre and post-execution hooks
- **🌐 Multi-language Support**: Python, Node.js, and shell scripts
- **⚡ Concurrent Control**: Prevent system overload with execution limits
- **📄 LibreOffice Integration**: Document processing capabilities

## 🏗️ Architecture

### System Architecture
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

### Code Structure (v1.4.0)
The codebase is now organized in a modular structure for better maintainability:

```
PyExecutorHub/
├── api.py                 # Main FastAPI application entry point
├── routes/                # API route modules (organized by endpoint)
│   ├── auth.py           # Authentication routes (/auth)
│   ├── programs.py       # Program management routes (/programs)
│   ├── executions.py     # Execution routes (/executions)
│   ├── containers.py     # Container monitoring routes (/containers)
│   └── images.py         # Docker image routes (/images)
├── services/              # Business logic services
│   ├── auth_service.py   # Authentication service
│   ├── config_service.py # Configuration management
│   ├── execution_service.py  # Program execution logic
│   └── execution_storage.py  # Execution storage management
├── models/                # Pydantic models
│   ├── auth_models.py    # Authentication models
│   ├── execution_models.py  # Execution models
│   └── program_models.py # Program models
├── utils/                 # Utility modules
│   ├── docker_utils.py   # Docker operations
│   └── log_formatter.py  # Log formatting utilities
├── scripts/               # Example scripts
├── bots/                  # Example bots
├── actions/               # Pre/post execution hooks
├── config.yaml            # Program configuration
└── docker-compose.yml     # Docker orchestration
```

### Benefits of Modular Architecture
- ✅ **Separation of Concerns**: Each module has a single responsibility
- ✅ **Easy Maintenance**: Changes to one endpoint don't affect others
- ✅ **Scalability**: Add new endpoints without modifying core files
- ✅ **Testability**: Each module can be tested independently
- ✅ **Reusability**: Services and utilities can be reused across routes

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

# Start the system (builds both base image and API)
docker compose up -d --build

# Or use the installer script
chmod +x install.sh
./install.sh
```

### Automated Installation
Use the provided installer script for a complete setup:

```bash
# Make script executable
chmod +x install.sh

# Run installer
./install.sh
```

The installer will:
- ✅ Check system requirements
- ✅ Configure environment
- ✅ Build base image with LibreOffice
- ✅ Build and start API service
- ✅ Test the installation
- ✅ Show usage instructions

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

## 🔐 Authentication

### Overview
PyExecutorHub now includes a secure authentication system that generates random credentials at startup and uses JWT tokens for API access.

### Security Features
- **🔑 Random Credentials**: Username and password generated automatically at startup
- **🎫 JWT Tokens**: Secure token-based authentication for API access
- **⏰ Token Expiration**: Tokens expire after 24 hours for security
- **🛡️ Endpoint Protection**: All API endpoints require authentication
- **🔒 One-time Display**: Credentials shown only once at startup

### Getting Started

#### 1. **Start the System**
```bash
docker compose up -d --build
```

#### 2. **Get Credentials**
The system will display credentials at startup:
```
🔐 CREDENCIALES DE USO
============================================================
👤 Usuario: abc123def
🔑 Password: xY9#mK2$pL8
============================================================
💡 Usa estas credenciales para hacer login en /auth/login
🔒 Las credenciales solo se muestran una vez por seguridad
============================================================
```

#### 3. **Login to Get Token**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "abc123def", "password": "xY9#mK2$pL8"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "username": "abc123def"
}
```

#### 4. **Use Token for API Calls**
```bash
# Get programs list
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/programs

# Execute a program
curl -X POST http://localhost:8001/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"program_id": "example_script"}'
```

### Authentication Endpoints

#### Login
- **POST** `/auth/login`
- **Body**: `{"username": "string", "password": "string"}`
- **Response**: JWT token and user information

### Security Notes
- **Credentials are generated once** at startup and shown only once
- **No endpoint to retrieve credentials** after startup for security
- **Tokens expire after 24 hours** and must be renewed
- **All API endpoints require authentication** except `/health` and `/auth/login`

## Configuration

The system uses a `config.yaml` file to define available scripts and bots. This file is mounted as a volume, allowing you to modify the configuration without rebuilding the container.

### Configuration File Structure

```yaml
scripts:
  # Example 1: Basic script without custom Docker image
  example_script:
    id: "example_script"
    name: "Example Script"
    path: "scripts/example_script"  # Relative path
    description: "Example script without custom Docker image"
    enabled: true
    main_file: "main.py"
    # docker_image: Not specified, uses default
    # parameters: Not specified, runs without parameters

  # Example 2: Script with custom Docker image
  script_with_custom_image:
    id: "script_with_custom_image"
    name: "Script with Custom Docker Image"
    path: "scripts/custom_script"
    description: "Script that uses a custom Docker image"
    enabled: true
    main_file: "run.py"
    docker_image: "custom-image:latest"  # Custom Docker image

  # Example 3: Script with parameters
  script_with_parameters:
    id: "script_with_parameters"
    name: "Script with Parameters"
    path: "scripts/parameterized_script"
    description: "Script that accepts command-line parameters"
    enabled: true
    main_file: "main.py"
    parameters: "--process proceso_2 --verbose"  # Command-line parameters

  # Example 4: External script (requires volume mount)
  external_script:
    id: "external_script"
    name: "External Script"
    path: "/docker/scripts/external_script"  # Absolute path
    description: "Script located outside the project directory"
    enabled: true
    main_file: "run.py"
    docker_image: "external-script:latest"

bots:
  example_bot:
    id: "example_bot"
    name: "Example Bot"
    path: "bots/example_bot"
    description: "Example bot"
    enabled: true
    main_file: "run.py"
    parameters: "--mode production --verbose"

# General system configuration
settings:
  docker_image: "pyexecutorhub-base"  # Default image for programs without custom image
  timeout_seconds: 300  # 5 minutes default
  max_concurrent_executions: 5 
  memory_limit: "1g"    # Recommended: 1GB for most cases
  cpu_limit: "0.5"      # CPU limit per container (50% of one core)
```

### Configuration Options

#### Required Fields
- `id`: Unique identifier for the program
- `name`: Descriptive name
- `path`: Path to program directory (relative or absolute)
- `description`: Program description
- `enabled`: `true` or `false` to enable/disable
- `main_file`: Main file to execute (`main.py`, `run.py`, `app.js`, etc.)

#### Optional Fields
- `docker_image`: Custom Docker image (if not specified, uses default)
- `parameters`: Command-line parameters to pass to the program
- `path_docker_compose_run`: Path to docker-compose file for docker compose execution (alternative to docker run)

### Docker Compose Execution

PyExecutorHub supports executing programs using `docker compose up` instead of the standard `docker run` method. This is useful for complex multi-container applications or when you need to orchestrate multiple services.

#### Configuration

Add `path_docker_compose_run` to your program configuration:

```yaml
scripts:
  docker_compose_script:
    id: "docker_compose_script"
    name: "Docker Compose Script"
    path: "scripts/docker_compose_script"
    description: "Script that uses docker compose up"
    enabled: true
    path_docker_compose_run: "docker-compose.yml"  # Path to docker-compose file
```

#### How It Works

When `path_docker_compose_run` is present:
- ✅ The system executes `docker compose -f <path> up` instead of `docker run`
- ✅ `docker_image` and `main_file` are **ignored** (not used)
- ✅ The docker-compose file is executed in its directory context
- ✅ Services are automatically cleaned up with `docker compose down` after execution
- ✅ All logs and output are captured and returned

#### Path Resolution

The `path_docker_compose_run` can be:
- **Relative**: Relative to the program's `path` directory
  ```yaml
  path: "scripts/my_script"
  path_docker_compose_run: "docker-compose.yml"  # Resolves to scripts/my_script/docker-compose.yml
  ```
- **Absolute**: Full path to the docker-compose file
  ```yaml
  path: "scripts/my_script"
  path_docker_compose_run: "/docker/scripts/my_script/docker-compose.yml"  # Absolute path
  ```

#### Example: Docker Compose Script

**1. Directory structure:**
```
scripts/
  └── docker_compose_script/
      ├── docker-compose.yml
      └── app/
          └── main.py
```

**2. docker-compose.yml:**
```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - PROGRAM_ID=${PROGRAM_ID}
      - EXECUTION_ID=${EXECUTION_ID}
    volumes:
      - ./app:/app
```

**3. config.yaml:**
```yaml
scripts:
  docker_compose_script:
    id: "docker_compose_script"
    name: "Docker Compose Script"
    path: "scripts/docker_compose_script"
    description: "Multi-container application"
    enabled: true
    path_docker_compose_run: "docker-compose.yml"  # Relative to path
```

#### Important Notes

- **Automatic Cleanup**: The system automatically runs `docker compose down` after execution to clean up services
- **Timeout Handling**: If execution times out, cleanup is still attempted
- **Environment Variables**: `PROGRAM_ID` and `EXECUTION_ID` are available in the docker-compose context
- **Concurrent Limits**: Docker compose executions count towards the concurrent execution limit
- **Logs**: All output from `docker compose up` is captured and returned in the execution logs

### External Scripts and Bots (Volume Mounting)

If your scripts or bots are located **outside** the PyExecutorHub project directory, you need to mount them as volumes in `docker-compose.yml`.

#### Step 1: Configure the Path in config.yaml

Use an **absolute path** in your configuration:

```yaml
scripts:
  external_script:
    id: "external_script"
    name: "External Script"
    path: "/docker/scripts/external_script"  # Absolute path
    description: "Script located outside project"
    enabled: true
    main_file: "run.py"
    docker_image: "external-script:latest"
```

#### Step 2: Add Volume to docker-compose.yml

Add the volume mount in the `pyexecutorhub-api` service:

```yaml
services:
  pyexecutorhub-api:
    # ... other configuration ...
    volumes:
      - .:/project:ro
      - ./config.yaml:/app/config.yaml:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker:ro
      - /docker/scripts:/docker/scripts:ro  # Mount external scripts directory
```

#### Important Notes

- **Read-Only Mount**: Use `:ro` flag for security (read-only access)
- **Path Consistency**: The path in `config.yaml` must match the volume mount path
- **Permissions**: Ensure the Docker container has read permissions for the mounted directory
- **Multiple Directories**: You can mount multiple external directories:

```yaml
volumes:
  - /docker/scripts:/docker/scripts:ro
  - /external/bots:/external/bots:ro
  - /custom/path:/custom/path:ro
```

#### Example: Complete Setup for External Scripts

**1. Directory structure on host:**
```
/docker/scripts/
  ├── extractcredentialsfromemail/
  │   ├── run.py
  │   └── .env
  └── photovalidator/
      ├── run.py
      └── requirements.txt
```

**2. config.yaml:**
```yaml
scripts:
  extractcredentialsfromemail:
    id: "1"
    name: "Extractor de creds"
    path: "/docker/scripts/extractcredentialsfromemail"  # Absolute path
    description: "Script scrapping de Emails"
    enabled: true
    main_file: "run.py"
    docker_image: "extractcredentialsfromemail:latest"

  photovalidator:
    id: "18"
    name: "Screenshot Validator"
    path: "/docker/scripts/photovalidator"  # Absolute path
    description: "Valida la imagen"
    enabled: true
    main_file: "run.py"
    docker_image: "photovalidator:latest"
```

**3. docker-compose.yml:**
```yaml
services:
  pyexecutorhub-api:
    volumes:
      - .:/project:ro
      - ./config.yaml:/app/config.yaml:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker:ro
      - /docker/scripts:/docker/scripts:ro  # External scripts volume
```

### Real-time Configuration Updates

The `config.yaml` file is mounted as a volume, which means:
- ✅ **No rebuild required**: Changes to the configuration file are reflected immediately
- ✅ **Live updates**: Add, modify, or remove programs without restarting the container
- ✅ **Persistent changes**: Configuration changes survive container restarts
- ✅ **Easy management**: Edit the file directly on the host system

To add a new program:
1. Edit `config.yaml` and add your program configuration
2. If using external scripts, ensure the volume is mounted in `docker-compose.yml`
3. The new program will be available immediately via the API
4. No container restart or rebuild needed

## 📋 Parameterized Execution

### Overview
PyExecutorHub now supports parameterized program execution, allowing you to configure command-line parameters for each program in the configuration file.

### Configuration
Add a `parameters` field to your program configuration:

```yaml
scripts:
  example_script:
    id: "example_script"
    name: "Example Script"
    path: "scripts/example_script"
    description: "Example script with parameters"
    enabled: true
    main_file: "main.py"
    parameters: "--process proceso_2 --verbose"  # Optional parameters

bots:
  data_processor:
    id: "data_processor"
    name: "Data Processor"
    path: "bots/data_processor"
    description: "Process data with custom parameters"
    enabled: true
    main_file: "run.py"
    parameters: "--input data.csv --output results.json --format json"
```

### How It Works
When a program is executed, the system automatically appends the configured parameters to the command:

**Without parameters:**
```bash
python main.py
```

**With parameters:**
```bash
python main.py --process proceso_2 --verbose
```

### Multi-language Support
Parameters work with different file types:

#### Python Scripts
```yaml
parameters: "--verbose --output /tmp/result.txt"
# Executes: python main.py --verbose --output /tmp/result.txt
```

#### Node.js Scripts
```yaml
parameters: "--mode production --port 8080"
# Executes: node main.js --mode production --port 8080
```

#### Shell Scripts
```yaml
parameters: "--config /etc/app.conf --debug"
# Executes: bash script.sh --config /etc/app.conf --debug
```

### Examples

#### Basic Parameters
```yaml
my_script:
  parameters: "--verbose"
```

#### Multiple Parameters
```yaml
api_client:
  parameters: "--host api.example.com --port 8080 --timeout 30"
```

#### Complex Parameters
```yaml
data_processor:
  parameters: "--input data.csv --output results.json --format json --compress"
```

### Program Implementation
Your programs can access command-line arguments using standard methods:

#### Python Example
```python
#!/usr/bin/env python3
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='My Program')
    parser.add_argument('--process', help='Process name')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print(f"Process: {args.process}")
    print(f"Verbose: {args.verbose}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

#### Node.js Example
```javascript
#!/usr/bin/env node
const args = process.argv.slice(2);
const processName = args.find(arg => arg.startsWith('--process'))?.split('=')[1];
const verbose = args.includes('--verbose');

console.log(`Process: ${processName}`);
console.log(`Verbose: ${verbose}`);
```

### Logging
The system logs parameter usage for debugging:

```
📋 Program parameters: --process proceso_2 --verbose
🐳 Docker command: ... python main.py --process proceso_2 --verbose ...
```

### Best Practices
1. **Use descriptive parameter names** for clarity
2. **Document parameters** in your program's help text
3. **Validate parameters** in your program code
4. **Use consistent naming** across similar programs
5. **Test parameters** before production deployment

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

### Base Image Features
The default `pyexecutorhub-base` image includes:

#### Python Environment
- **Python 3.11** with latest pip
- **MariaDB driver** for database connections
- **System dependencies** for common Python packages

#### LibreOffice Suite
- **LibreOffice Writer** - Document processing
- **LibreOffice Calc** - Spreadsheet operations
- **LibreOffice Impress** - Presentation creation
- **LibreOffice Draw** - Vector graphics
- **LibreOffice Math** - Formula editing
- **LibreOffice Base** - Database management

#### Usage Examples
```python
#!/usr/bin/env python3
import subprocess
import os

def convert_document():
    """Convert a document using LibreOffice"""
    input_file = "/workspace/document.docx"
    output_dir = "/workspace/output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert document to PDF
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_file
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Document converted successfully")
    else:
        print(f"❌ Conversion failed: {result.stderr}")
    
    return result.returncode

if __name__ == "__main__":
    exit(convert_document())
```

### Building Images

#### Build Base Image Only
```bash
# Build only the base image with LibreOffice
docker compose build pyexecutorhub-base
```

#### Build API Service Only
```bash
# Build only the API service
docker compose build pyexecutorhub-api
```

#### Build All Images
```bash
# Build both base image and API service
docker compose build
```

#### Rebuild and Start
```bash
# Rebuild and start all services
docker compose up -d --build
```

### Best Practices
1. **Use specific versions** instead of `latest`
2. **Choose lightweight images** when possible
3. **Test your images** before production
4. **Document image requirements** in your code
5. **Use multi-stage builds** for complex setups
6. **Leverage LibreOffice** for document processing tasks
7. **Build base image first** when making changes to dependencies

## 📖 Usage

### API Endpoints

#### 1. Login to Get Token
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}'
```

#### 2. List Programs (with parameters)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/programs
```

#### 3. Execute Program (with configured parameters)
```bash
curl -X POST http://localhost:8001/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"program_id": "example_script"}'
```

#### 4. Check Execution Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/executions/{execution_id}
```

#### 5. Get Detailed Statistics
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/executions/stats
```

#### Complete Example
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "abc123def", "password": "xY9#mK2$pL8"}' | jq -r '.access_token')

# 2. List programs
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/programs

# 3. Execute program with parameters
curl -X POST http://localhost:8001/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"program_id": "example_script"}'

# 4. Check status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/executions/{execution_id}
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

### Authentication Endpoints
- `POST /auth/login` - Login to get JWT token
- `GET /health` - Health check (no authentication required)

### Core Endpoints (Authentication Required)
- `GET /` - API information
- `GET /programs` - List all programs with parameters
- `POST /execute` - Execute a program with parameters
- `GET /executions` - List all executions
- `GET /executions/{id}` - Get execution status

### Management Endpoints (Authentication Required)
- `GET /executions/info` - Execution statistics
- `GET /executions/stats` - Detailed statistics by status and program
- `GET /executions/concurrent` - Concurrent execution information
- `DELETE /executions/cleanup` - Cleanup finished executions

### Container Monitoring Endpoints (Authentication Required)
- `GET /containers/logs/{image_name}` - Get logs from containers by Docker image
- `GET /containers/active` - Get all active containers
- `GET /executions/{execution_id}/logs` - Get detailed execution logs with timing

### Docker Images Endpoints (Authentication Required)
- `GET /images/available` - Get all available Docker images from configuration
- `GET /images/search/{image_name}` - Search for specific Docker images in configuration

### Authentication Header
All protected endpoints require the following header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

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
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/executions/{execution_id}/logs

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

### Detailed Statistics
Get comprehensive execution statistics with program breakdown:

```bash
# Get detailed statistics
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/executions/stats

# Response
{
  "total": 395,
  "by_status": {
    "completed": [
      {"total": 350, "name": "example_script"},
      {"total": 200, "name": "data_processor"},
      {"total": 150, "name": "test_script"}
    ],
    "failed": [
      {"total": 4, "name": "example_script"},
      {"total": 2, "name": "data_processor"}
    ],
    "timeout": [
      {"total": 1, "name": "long_running_script"}
    ],
    "running": [
      {"total": 2, "name": "example_script"}
    ],
    "queued": [
      {"total": 1, "name": "data_processor"}
    ]
  }
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

#### Authentication Issues
```bash
# Check if API is running
curl http://localhost:8001/health

# Get credentials from logs
docker compose logs pyexecutorhub-api | grep -A 5 "CREDENCIALES DE USO"

# Test login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}'
```

#### Program Not Found
```bash
# Login first
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "YOUR_USERNAME", "password": "YOUR_PASSWORD"}' | jq -r '.access_token')

# Check if program exists
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/programs

# Verify configuration
cat config.yaml
```

#### Execution Failures
```bash
# Check execution status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/executions/{execution_id}

# View container logs
docker logs pyexecutorhub-api
```

#### Parameter Issues
```bash
# Check if parameters are configured
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/programs | jq '.[] | {id, name, parameters}'

# Check execution logs for parameter usage
docker compose logs pyexecutorhub-api | grep "Program parameters"
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
2. **Get credentials**: `docker compose logs pyexecutorhub-api | grep -A 5 "CREDENCIALES"`
3. **Login and get token**: Use the credentials to get a JWT token
4. **Verify configuration**: Review `config.yaml` for parameters
5. **Check Docker**: `docker ps -a`
6. **View logs**: `docker logs pyexecutorhub-api`
7. **Test manually**: Run program directly in container

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