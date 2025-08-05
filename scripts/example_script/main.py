#!/usr/bin/env python3
"""
Example Script for PyExecutorHub
Simple script that uses the default Docker image
"""

import os
import sys
from datetime import datetime

def main():
    """Main function that demonstrates basic script functionality"""
    
    # Get environment variables
    program_id = os.getenv('PROGRAM_ID', 'unknown')
    execution_id = os.getenv('EXECUTION_ID', 'unknown')
    
    # Get current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 50)
    print("📝 Example Script")
    print("=" * 50)
    print(f"⏰ Execution Time: {current_time}")
    print(f"📋 Program ID: {program_id}")
    print(f"🆔 Execution ID: {execution_id}")
    print("=" * 50)
    
    # Check if running in Docker
    if os.path.exists('/.dockerenv'):
        print("🐳 Running inside Docker container")
    else:
        print("💻 Running on host system")
    
    # Display Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check for custom parameters
    param_count = 0
    for key, value in os.environ.items():
        if key.startswith('PARAM_'):
            param_count += 1
            print(f"📝 Parameter {key}: {value}")
    
    if param_count == 0:
        print("📝 No custom parameters provided")
    
    # Simple example logic
    print("🔧 Performing example task...")
    print("✅ Example script completed successfully!")
    print("=" * 50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 