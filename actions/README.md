# 🔧 PyExecutorHub Actions System (Hooks)

This directory contains actions that run automatically **before** and **after** each program (script or bot) in PyExecutorHub.

## 📁 Structure

```
actions/
├── act_before.py      # Actions that run BEFORE the program
├── act_after.py       # Actions that run AFTER the program
├── requirements.txt   # Dependencies for actions
└── README.md         # This documentation
```

## 🔄 Execution Flow

```
1. Execution request received
2. Docker container created
3. 🔧 act_before.py runs (validations, logging)
4. 🚀 Main program executes
5. 🔧 act_after.py runs (notifications, cleanup)
6. Result returned
```

## 📋 Available Environment Variables

Actions have access to these environment variables:

- `PROGRAM_ID`: ID of the program being executed
- `EXECUTION_ID`: Unique execution ID
- `EXIT_CODE`: Exit code (only in act_after.py)
- `PARAM_*`: Parameters passed to the program

## 🔧 act_before.py

**Purpose:** Actions that run BEFORE the main program.

**Use cases:**
- ✅ Environment validations
- ✅ Resource verification (disk space, memory)
- ✅ Network connectivity verification
- ✅ Temporary file cleanup
- ✅ Create necessary directories
- ✅ Startup logging
- ✅ Startup notifications

**Usage example:**
```python
def main():
    # Check disk space
    if free_space < 1_GB:
        print("⚠️ Low disk space")
    
    # Check connectivity
    if not network_available():
        print("⚠️ No network connectivity")
    
    # Create logs directory
    Path("/workspace/logs").mkdir(exist_ok=True)
```

## 🔧 act_after.py

**Purpose:** Actions that run AFTER the main program.

**Use cases:**
- ✅ Completion logging
- ✅ Result notifications
- ✅ Temporary file cleanup
- ✅ Result backup
- ✅ Metrics sending
- ✅ Log analysis

**Usage example:**
```python
def main():
    success = os.getenv('EXIT_CODE') == '0'
    
    if success:
        # Backup results
        backup_results()
        # Success notification
        send_success_notification()
    else:
        # Error notification
        send_error_notification()
        # Log analysis
        analyze_error_logs()
```

## ⚠️ Important Considerations

### 1. Error Handling
- Actions must handle their own errors
- An error in actions should NOT affect the main program
- Use try/catch for critical operations

### 2. Execution Time
- Actions run within the same timeout as the program
- Keep actions light and fast
- Avoid long blocking operations

### 3. Resources
- Actions share resources with the main program
- Don't consume too much memory or CPU
- Clean up resources after use

### 4. Logging
- Use clear prefixes: `[ACT_BEFORE]` or `[ACT_AFTER]`
- Logs appear in the program output
- Use emojis for better readability

## 🚀 Customization

### Adding New Actions

1. **Edit the corresponding file:**
   ```bash
   nano actions/act_before.py
   # or
   nano actions/act_after.py
   ```

2. **Add your logic in the `main()` function:**
   ```python
   def main():
       # Your code here
       pass
   ```

3. **Install dependencies if necessary:**
   ```bash
   echo "your-dependency==1.0.0" >> actions/requirements.txt
   ```

### Disabling Actions

To temporarily disable actions, rename the files:
```bash
mv actions/act_before.py actions/act_before.py.disabled
mv actions/act_after.py actions/act_after.py.disabled
```

## 📊 Monitoring

### View Action Logs
```bash
# View logs of a specific execution
curl http://localhost:8000/executions/{execution_id}

# Action logs appear in the output
```

### Example Output
```
🔧 Executing pre-execution actions...
🔧 [ACT_BEFORE] Starting pre-execution actions...
📋 [ACT_BEFORE] Program: example_script
🆔 [ACT_BEFORE] Execution: 123e4567-e89b-12d3-a456-426614174000
⏰ [ACT_BEFORE] Timestamp: 2025-07-02T09:10:00.000000
💾 [ACT_BEFORE] Free space: 15 GB
🌐 [ACT_BEFORE] Network connectivity: OK
✅ [ACT_BEFORE] Pre-execution actions completed

🚀 Script running...
✅ Script completed successfully!

🔧 Executing post-execution actions...
🔧 [ACT_AFTER] Starting post-execution actions...
📋 [ACT_AFTER] Program: example_script
🆔 [ACT_AFTER] Execution: 123e4567-e89b-12d3-a456-426614174000
🔚 [ACT_AFTER] Exit code: 0
📊 [ACT_AFTER] Status: ✅ SUCCESSFUL
📝 [ACT_AFTER] Log saved: /workspace/logs/execution_123e4567-e89b-12d3-a456-426614174000.log
📧 [ACT_AFTER] Notification: Execution completed successfully
✅ [ACT_AFTER] Post-execution actions completed
```

## 🔧 Troubleshooting

### Problem: Actions not running
- Verify files exist: `ls -la actions/`
- Check permissions: `chmod +x actions/*.py`
- Check container logs: `docker logs serverless-docker-api`

### Problem: Dependency errors
- Check `actions/requirements.txt`
- Verify dependencies are compatible
- Test manual installation: `pip install -r actions/requirements.txt`

### Problem: Environment variables not available
- Verify `PROGRAM_ID` and `EXECUTION_ID` are defined
- Use default values: `os.getenv('PROGRAM_ID', 'unknown')`

---

**⚡ PyExecutorHub - Deploy Python scripts in seconds, execute with confidence.** 