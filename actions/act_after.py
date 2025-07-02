#!/usr/bin/env python3
"""
Actions that run AFTER each program
This file runs after completing any script or bot
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    """
    Main function that runs after each program
    Here you can add:
    - Completion logging
    - Result notifications
    - Resource cleanup
    - Metrics sending
    - Result backup
    - etc.
    """
    
    print("🔧 [ACT_AFTER] Starting post-execution actions...")
    
    # Get information about the program that was executed
    program_id = os.getenv('PROGRAM_ID', 'unknown')
    execution_id = os.getenv('EXECUTION_ID', 'unknown')
    exit_code = os.getenv('EXIT_CODE', '0')
    
    print(f"📋 [ACT_AFTER] Program: {program_id}")
    print(f"🆔 [ACT_AFTER] Execution: {execution_id}")
    print(f"🔚 [ACT_AFTER] Exit code: {exit_code}")
    print(f"⏰ [ACT_AFTER] Timestamp: {datetime.now().isoformat()}")
    
    # Determine if execution was successful
    success = exit_code == '0'
    status = "✅ SUCCESSFUL" if success else "❌ FAILED"
    print(f"📊 [ACT_AFTER] Status: {status}")
    
    # TODO: Add your custom actions here
    # Examples:
    # - Create log file with result
    # - Send success/error notification
    # - Clean temporary files
    # - Record resource usage metrics
    # - Backup important files
    # - Send metrics to monitoring system
    # - etc.
    
    print("✅ [ACT_AFTER] Post-execution actions completed")
    
    # IMPORTANT: If something fails critically, you can use sys.exit(1)
    # but keep in mind this won't affect the main program's result
    # if critical_error:
    #     print("❌ [ACT_AFTER] Critical error in post-execution actions")
    #     sys.exit(1)

if __name__ == "__main__":
    main() 