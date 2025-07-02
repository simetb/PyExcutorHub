#!/usr/bin/env python3
"""
Example script for the Serverless System
Demonstrates how to create a script that runs in the serverless environment
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def main():
    """Main function of the script"""
    print("=" * 50)
    print("🚀 EXAMPLE SCRIPT - SERVERLESS SYSTEM")
    print("=" * 50)
    
    # Environment information
    print(f"📅 Date and time: {datetime.now()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"👤 User: {os.getenv('USER', 'unknown')}")
    
    # System environment variables
    print("\n🔧 System environment variables:")
    system_vars = {
        'PYTHONUNBUFFERED': os.getenv('PYTHONUNBUFFERED'),
        'PROJECT_DIR': os.getenv('PROJECT_DIR'),
        'HOST_PROJECT_DIR': os.getenv('HOST_PROJECT_DIR'),
    }
    for key, value in system_vars.items():
        print(f"  {key}: {value}")
    
    # Parameters sent from the API
    print("\n📋 Parameters received:")
    parameters = {}
    for key, value in os.environ.items():
        if key.startswith('PARAM_'):
            param_name = key[6:]  # Remove 'PARAM_' prefix
            parameters[param_name] = value
            print(f"  {param_name}: {value}")
    
    if not parameters:
        print("  No parameters received")
    
    # Script-specific environment variables (from .env)
    print("\n🔐 Script environment variables:")
    script_vars = {
        'API_KEY': os.getenv('API_KEY'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'DEBUG': os.getenv('DEBUG'),
    }
    for key, value in script_vars.items():
        if value:
            print(f"  {key}: {'*' * len(value)}")  # Hide sensitive values
        else:
            print(f"  {key}: Not defined")
    
    # Simulate script work
    print("\n⚙️ Executing script logic...")
    
    # Example: process parameters
    if parameters:
        print("  Processing received parameters...")
        for name, value in parameters.items():
            print(f"    Processing {name}: {value}")
    
    # Example: check files in directory
    print("  Checking files in directory...")
    current_dir = Path('.')
    files = list(current_dir.glob('*'))
    print(f"    Files found: {len(files)}")
    
    # Example: simulate work
    import time
    print("  Simulating work...")
    for i in range(3):
        print(f"    Step {i+1}/3...")
        time.sleep(1)
    
    # Final result
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "parameters_processed": len(parameters),
        "files_found": len(files),
        "python_version": sys.version,
        "working_directory": os.getcwd()
    }
    
    print("\n📊 Script result:")
    print(json.dumps(result, indent=2))
    
    print("\n✅ Script completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        print(f"Error occurred: {datetime.now()}")
        sys.exit(1) 