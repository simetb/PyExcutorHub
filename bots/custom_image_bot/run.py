#!/usr/bin/env python3
"""
Custom Image Bot Example
This bot demonstrates using a custom Docker image (python:3.12-alpine)
"""

import os
import sys
import platform
import subprocess

def main():
    print("🚀 Custom Image Bot Started")
    print("=" * 50)
    
    # Show system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Show environment variables
    print("\n📋 Environment Variables:")
    print(f"PROGRAM_ID: {os.getenv('PROGRAM_ID', 'Not set')}")
    print(f"EXECUTION_ID: {os.getenv('EXECUTION_ID', 'Not set')}")
    
    # Show custom parameters
    print("\n🔧 Custom Parameters:")
    for key, value in os.environ.items():
        if key.startswith('PARAM_'):
            param_name = key[6:]  # Remove 'PARAM_' prefix
            print(f"  {param_name}: {value}")
    
    # Check if we're running in a container
    try:
        with open('/proc/1/cgroup', 'r') as f:
            cgroup = f.read()
            if 'docker' in cgroup:
                print("\n✅ Running inside Docker container")
            else:
                print("\n❌ Not running inside Docker container")
    except:
        print("\n⚠️ Could not determine if running in container")
    
    # Show available Python packages
    print("\n📦 Installed Python packages:")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Could not list packages")
    except Exception as e:
        print(f"Error listing packages: {e}")
    
    # Show system resources
    print("\n💻 System Resources:")
    try:
        import psutil
        print(f"CPU cores: {psutil.cpu_count()}")
        print(f"Total memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f} GB")
        print(f"Free memory: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.2f} GB")
    except ImportError:
        print("psutil not available for system resource info")
    
    print("\n✅ Custom Image Bot completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 