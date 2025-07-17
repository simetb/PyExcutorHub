#!/usr/bin/env python3
"""
Serverless Docker API
FastAPI for executing scripts and bots in Docker containers
"""

import asyncio
import json
import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
import yaml
from dotenv import dotenv_values
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

# Pydantic models for responses
class ExecutionRequest(BaseModel):
    program_id: str = Field(..., description="ID of the program to execute")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Additional parameters")

class ExecutionResponse(BaseModel):
    execution_id: str
    program_id: str
    status: str
    message: str
    timestamp: datetime

class ProgramInfo(BaseModel):
    id: str
    name: str
    type: str
    description: str
    enabled: bool
    path: str
    key: Optional[str] = None

class ExecutionStatus(BaseModel):
    execution_id: str
    program_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None

# Global state for execution tracking
executions: Dict[str, ExecutionStatus] = {}
MAX_EXECUTIONS = 100  # Memory execution limit

# No more lock - we'll use simple atomic operations

class ServerlessAPI:
    def __init__(self):
        print("🚀 Initializing ServerlessAPI...")
        self.app = FastAPI(
            title="Serverless Docker API",
            description="API for executing scripts and bots in isolated Docker containers",
            version="1.0.0"
        )
        print("📋 FastAPI app created")
        self.config = self.load_config()
        print("⚙️ Config loaded")
        self.docker_image = self.config.get("settings", {}).get("docker_image", "serverless-base")
        # In Docker, the base directory is /app
        self.base_dir = Path("/app")
        print("🔧 Setting up routes...")
        self.setup_routes()
        print("✅ ServerlessAPI initialization complete")
    
    def load_config(self) -> Dict:
        """Load configuration from config.yaml"""
        config_path = Path("/app/config.yaml")
        if not config_path.exists():
            raise FileNotFoundError("config.yaml not found")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_program_by_id(self, program_id: str) -> Optional[Dict]:
        """Find a program by ID in the configuration"""
        # Search in scripts by key or internal id
        for script_id, script_config in self.config.get("scripts", {}).items():
            if script_id == program_id or script_config.get("id") == program_id:
                script_config["type"] = "script"
                return script_config
        
        # Search in bots by key or internal id
        for bot_id, bot_config in self.config.get("bots", {}).items():
            if bot_id == program_id or bot_config.get("id") == program_id:
                bot_config["type"] = "bot"
                return bot_config
        
        return None
    
    def build_image(self):
        """Build the base Docker image if it doesn't exist"""
        try:
            result = subprocess.run(
                ["docker", "images", "-q", self.docker_image],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                print(f"🔨 Building Docker image: {self.docker_image}")
                # Use the project directory mounted in the container
                project_dir = "/project"
                print(f"📁 Building from: {project_dir}")
                subprocess.run(
                    ["docker", "build", "-t", self.docker_image, project_dir],
                    check=True
                )
                print("✅ Image built successfully")
            else:
                print(f"✅ Image {self.docker_image} already exists")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building Docker image: {e}")
            raise HTTPException(status_code=500, detail=f"Error building Docker image: {e}")
    
    def get_env_vars(self, program_path: Path) -> Dict[str, str]:
        """Read environment variables from the program's .env file"""
        env_file = program_path / ".env"
        if env_file.exists():
            print(f"📄 Loading environment variables from: {env_file}")
            return dotenv_values(env_file)
        return {}
    
    def format_logs(self, log_content: str) -> str:
        """Format log content to display properly with line breaks"""
        if not log_content:
            return ""
        
        # Replace literal \n with actual line breaks
        # Also handle other common escape sequences
        formatted = log_content.replace('\\n', '\n')
        formatted = formatted.replace('\\t', '\t')
        formatted = formatted.replace('\\r', '\r')
        
        # Remove any trailing whitespace and normalize line endings
        formatted = formatted.rstrip()
        
        return formatted

    async def execute_program(self, execution_id: str, program_id: str, parameters: Dict = None):
        """Execute a program in background"""
        try:
            # Update status
            executions[execution_id] = ExecutionStatus(
                execution_id=execution_id,
                program_id=program_id,
                status="running",
                start_time=datetime.now()
            )
            
            # Get program configuration
            program_config = self.get_program_by_id(program_id)
            if not program_config:
                raise Exception(f"Program with ID '{program_id}' not found")
            
            if not program_config.get("enabled", True):
                raise Exception(f"Program '{program_id}' is disabled")
            
            # Use absolute host path for volume mounting
            host_project_dir = os.getenv("HOST_PROJECT_DIR", "/home/temis/Documents/fractalia/test_produccion")
            program_path = Path(program_config["path"])
            full_host_path = Path(host_project_dir) / program_path
            print(f"Mounting volume: {str(full_host_path)}:/workspace")
            
            # Don't verify host path existence from inside the container
            # Verification will be done when Docker command runs from host
            
            # Use main_file from configuration or default to main.py
            main_file_name = program_config.get("main_file", "main.py")
            # Don't verify file existence from inside the container
            # Docker command will run from host and have access to the file
            
            print(f"🚀 Executing program: {program_id} ({program_path}) with file: {main_file_name}")
            
            # Build image if necessary
            self.build_image()
            
            # Prepare Docker command using absolute host path
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{str(full_host_path)}:/workspace"
            ]
            
            # Add environment variables
            env_vars = self.get_env_vars(full_host_path)
            for key, value in env_vars.items():
                docker_cmd.extend(["-e", f"{key}={value}"])
            
            # Add environment variables for actions
            docker_cmd.extend(["-e", f"PROGRAM_ID={program_id}"])
            docker_cmd.extend(["-e", f"EXECUTION_ID={execution_id}"])
            
            # Add parameters as environment variables
            if parameters:
                for key, value in parameters.items():
                    docker_cmd.extend(["-e", f"PARAM_{key.upper()}={value}"])
            
            docker_cmd.extend([self.docker_image])
            
            # Build container command
            container_cmd = self._build_container_command(full_host_path, main_file_name)
            docker_cmd.append(container_cmd)
            
            print(f"🐳 Docker command: {' '.join(docker_cmd)}")
            print(f"🐳 Docker command to run: {docker_cmd}")
            
            # Execute container from host in a separate thread to avoid blocking the event loop
            def run_docker_command():
                return subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.config.get("settings", {}).get("timeout_seconds", 300)
                )
            
            result = await asyncio.to_thread(run_docker_command)
            
            # Update final status with properly formatted logs
            executions[execution_id].end_time = datetime.now()
            executions[execution_id].output = self.format_logs(result.stdout)
            executions[execution_id].error = self.format_logs(result.stderr)
            
            if result.returncode == 0:
                executions[execution_id].status = "completed"
                print(f"✅ Program {program_id} executed successfully")
            else:
                executions[execution_id].status = "failed"
                print(f"❌ Program {program_id} failed with code {result.returncode}")
            
        except subprocess.TimeoutExpired:
            executions[execution_id].status = "timeout"
            executions[execution_id].end_time = datetime.now()
            executions[execution_id].error = "Execution exceeded time limit"
            print(f"⏰ Program {program_id} exceeded time limit")
            
        except Exception as e:
            executions[execution_id].status = "failed"
            executions[execution_id].end_time = datetime.now()
            executions[execution_id].error = str(e)
            print(f"❌ Error executing program {program_id}: {e}")
    
    def _build_container_command(self, program_path: Path, main_file_name: str) -> str:
        """Build the command to execute inside the container"""
        commands = []
        
        # Change to working directory
        commands.append("cd /workspace")
        
        # Install dependencies if requirements.txt exists (will be verified inside container)
        commands.append("if [ -f requirements.txt ]; then pip install -r requirements.txt; fi")
        
        # Install action dependencies if they exist
        commands.append("if [ -f /project/actions/requirements.txt ]; then pip install -r /project/actions/requirements.txt; fi")
        
        # Execute action BEFORE the program
        commands.append("echo '🔧 Executing pre-execution actions...'")
        commands.append("if [ -f /project/actions/act_before.py ]; then python /project/actions/act_before.py; fi")
        
        # Execute the main program and capture exit code
        commands.append(f"python {main_file_name}")
        commands.append("EXIT_CODE=$?")
        
        # Set exit code as environment variable
        commands.append("export EXIT_CODE")
        
        # Execute action AFTER the program
        commands.append("echo '🔧 Executing post-execution actions...'")
        commands.append("if [ -f /project/actions/act_after.py ]; then python /project/actions/act_after.py; fi")
        
        # Return the exit code of the main program
        commands.append("exit $EXIT_CODE")
        
        return " && ".join(commands)
    
    async def cleanup_old_executions(self):
        """Remove oldest executions when limit is reached"""
        if len(executions) >= MAX_EXECUTIONS:
            # Only consider executions that are finished (completed, failed, timeout)
            # Don't remove running or queued executions
            finished_executions = [
                (exec_id, exec_status) for exec_id, exec_status in executions.items()
                if exec_status.status in ["completed", "failed", "timeout"]
            ]
            
            if len(finished_executions) > 0:
                # Sort by start_time and remove oldest finished executions
                sorted_executions = sorted(
                    finished_executions,
                    key=lambda x: x[1].start_time if x[1].start_time else datetime.min
                )
                
                # Calculate how many to remove
                to_remove = len(executions) - MAX_EXECUTIONS + 1
                
                # Remove oldest finished executions
                for i in range(min(to_remove, len(sorted_executions))):
                    exec_id = sorted_executions[i][0]
                    del executions[exec_id]
                    print(f"🗑️ Removed old execution: {exec_id}")
            else:
                # If no finished executions to remove, log a warning
                print(f"⚠️ Cannot cleanup: {len(executions)} executions exist but none are finished")
    
    async def manual_cleanup_executions(self):
        """Manually clean all finished executions"""
        initial_count = len(executions)
        
        # Find all finished executions
        finished_executions = [
            exec_id for exec_id, exec_status in executions.items()
            if exec_status.status in ["completed", "failed", "timeout"]
        ]
        
        # Remove all finished executions
        for exec_id in finished_executions:
            del executions[exec_id]
            print(f"🗑️ Manually removed execution: {exec_id}")
        
        final_count = len(executions)
        removed_count = initial_count - final_count
        
        return {
            "message": f"Manual cleanup completed",
            "removed_executions": removed_count,
            "remaining_executions": final_count,
            "max_executions": MAX_EXECUTIONS
        }
    
    async def add_execution(self, execution: ExecutionStatus):
        """Add a new execution and clean old ones if necessary"""
        executions[execution.execution_id] = execution
        await self.cleanup_old_executions()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint"""
            return {
                "message": "Serverless Docker API",
                "version": "1.0.0",
                "status": "running",
                "container": "docker"
            }
        
        @self.app.get("/health", response_model=Dict[str, str])
        async def health_check():
            """API health check"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/programs", response_model=List[ProgramInfo])
        async def list_programs():
            """List all available programs"""
            programs = []
            
            # Add scripts
            for script_id, script_config in self.config.get("scripts", {}).items():
                if script_config.get("enabled", True):
                    program_info = ProgramInfo(
                        id=script_config["id"],
                        name=script_config["name"],
                        type="script",
                        description=script_config.get("description", ""),
                        enabled=script_config.get("enabled", True),
                        path=script_config["path"]
                    )
                    # Add key as additional field
                    program_info.key = script_id
                    programs.append(program_info)
            
            # Add bots
            for bot_id, bot_config in self.config.get("bots", {}).items():
                if bot_config.get("enabled", True):
                    program_info = ProgramInfo(
                        id=bot_config["id"],
                        name=bot_config["name"],
                        type="bot",
                        description=bot_config.get("description", ""),
                        enabled=bot_config.get("enabled", True),
                        path=bot_config["path"]
                    )
                    # Add key as additional field
                    program_info.key = bot_id
                    programs.append(program_info)
            
            return programs
        
        @self.app.get("/test", response_model=Dict[str, str])
        async def test_endpoint():
            """Test endpoint to verify basic functionality"""
            print("🧪 Test endpoint called")
            return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/execute", response_model=ExecutionResponse)
        async def execute_program(request: ExecutionRequest, background_tasks: BackgroundTasks):
            """Execute a program"""
            print(f"🔍 Starting execution for program: {request.program_id}")
            
            # Verify program exists
            program_config = self.get_program_by_id(request.program_id)
            if not program_config:
                raise HTTPException(status_code=404, detail=f"Program with ID '{request.program_id}' not found")
            
            if not program_config.get("enabled", True):
                raise HTTPException(status_code=400, detail=f"Program '{request.program_id}' is disabled")
            
            print(f"✅ Program config found: {program_config['name']}")
            
            # Generate execution ID
            execution_id = str(uuid.uuid4())
            print(f"🆔 Generated execution ID: {execution_id}")
            
            # Create execution record
            execution = ExecutionStatus(
                execution_id=execution_id,
                program_id=request.program_id,
                status="queued",
                start_time=None,
                end_time=None,
                output=None,
                error=None
            )
            
            print(f"📝 Created execution record")
            
            # Execute in background
            background_tasks.add_task(
                self.execute_program,
                execution_id,
                request.program_id,
                request.parameters
            )
            
            print(f"🔄 Added background task")
            
            # Add execution to storage (simplified - no cleanup for now)
            executions[execution.execution_id] = execution
            print(f"💾 Added execution to storage")
            
            print(f"🎯 Returning response")
            
            return ExecutionResponse(
                execution_id=execution_id,
                program_id=request.program_id,
                status="queued",
                message=f"Program '{request.program_id}' queued for execution",
                timestamp=datetime.now()
            )
        
        @self.app.get("/executions", response_model=List[ExecutionStatus])
        async def list_executions():
            """List all executions"""
            print("🔍 /executions endpoint called")
            return list(executions.values())

        @self.app.get("/executions/info", response_model=Dict[str, Any])
        async def get_executions_info():
            """Get information about execution storage"""
            return {
                "total_executions": len(executions),
                "max_executions": MAX_EXECUTIONS,
                "available_slots": MAX_EXECUTIONS - len(executions),
                "storage_type": "memory",
                "cleanup_enabled": True
            }
        
        @self.app.get("/executions/stats", response_model=Dict[str, Any])
        async def get_executions_stats():
            """Get execution statistics"""
            if not executions:
                return {
                    "total": 0,
                    "by_status": {},
                    "recent_executions": 0,
                    "max_executions": MAX_EXECUTIONS
                }
            
            # Count by status
            status_counts = {}
            for execution in executions.values():
                status = execution.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count recent executions (last 24 hours)
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_count = sum(
                1 for execution in executions.values()
                if execution.start_time and execution.start_time > cutoff_time
            )
            
            return {
                "total": len(executions),
                "by_status": status_counts,
                "recent_executions": recent_count,
                "max_executions": MAX_EXECUTIONS
            }
        
        @self.app.delete("/executions/cleanup")
        async def cleanup_executions():
            """Manually clean all finished executions"""
            return await self.manual_cleanup_executions()
        
        @self.app.delete("/executions/manual_cleanup")
        async def manual_cleanup_executions_endpoint():
            """Manually clean all finished executions"""
            return await self.manual_cleanup_executions()
        
        @self.app.get("/executions/{execution_id}", response_model=ExecutionStatus)
        async def get_execution_status(execution_id: str):
            """Get execution status"""
            if execution_id not in executions:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            return executions[execution_id]

# Create API instance
api = ServerlessAPI()
app = api.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 