#!/usr/bin/env python3
"""
Serverless Docker API
FastAPI for executing scripts and bots in Docker containers
"""

import asyncio
import json
import os
import secrets
import string
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
import yaml
from dotenv import dotenv_values
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
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
    docker_image: Optional[str] = None  # Custom Docker image if specified
    parameters: Optional[str] = None  # Optional parameters for program execution

class ExecutionStatus(BaseModel):
    execution_id: str
    program_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None

# Authentication models
class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    username: str

class AuthCredentials(BaseModel):
    username: str
    password: str
    created_at: datetime

# Global state for execution tracking
executions: Dict[str, ExecutionStatus] = {}
MAX_EXECUTIONS = 100  # Memory execution limit

# Authentication configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Global auth credentials (generated at startup)
auth_credentials: Optional[AuthCredentials] = None

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
        # Don't load config here, load it on demand
        print("⚙️ Config will be loaded on demand")
        self.docker_image = "pyexecutorhub-base"  # Default, will be overridden by config
        # Use PROJECT_DIR environment variable or default to /app
        self.base_dir = Path(os.getenv("PROJECT_DIR", "/app"))
        print("🔧 Setting up routes...")
        self.setup_routes()
        print("✅ ServerlessAPI initialization complete")
    
    def generate_random_credentials(self) -> AuthCredentials:
        """Generate random username and password at startup"""
        # Generate random username (8 characters)
        username = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        
        # Generate random password (12 characters with mixed case, digits, and symbols)
        password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(password_chars) for _ in range(12))
        
        return AuthCredentials(
            username=username,
            password=password,
            created_at=datetime.now()
        )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the username"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
    
    def load_config(self) -> Dict:
        """Load configuration from config.yaml"""
        config_path = self.base_dir / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError("config.yaml not found")
        
        print(f"📄 Loading config from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # Update default docker image from config
            self.docker_image = config.get("settings", {}).get("docker_image", "pyexecutorhub-base")
            print(f"✅ Config loaded successfully, found {len(config.get('scripts', {}))} scripts and {len(config.get('bots', {}))} bots")
            return config
    
    def get_program_by_id(self, program_id: str) -> Optional[Dict]:
        """Find a program by ID in the configuration"""
        config = self.load_config()
        
        # Search in scripts by key or internal id
        for script_id, script_config in config.get("scripts", {}).items():
            if script_id == program_id or script_config.get("id") == program_id:
                script_config["type"] = "script"
                return script_config
        
        # Search in bots by key or internal id
        for bot_id, bot_config in config.get("bots", {}).items():
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
            host_project_dir = os.getenv("HOST_PROJECT_DIR", "/app")
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
            
            # Determine which Docker image to use
            # Priority: 1. Program-specific image, 2. Default image from settings
            docker_image = program_config.get("docker_image", self.docker_image)
            print(f"🐳 Using Docker image: {docker_image}")
            
            # Validate that the Docker image exists (optional check)
            if not await self._validate_docker_image(docker_image):
                print(f"⚠️ Warning: Docker image '{docker_image}' may not exist. Attempting to pull...")
                if not await self._pull_docker_image(docker_image):
                    raise Exception(f"Docker image '{docker_image}' not found and could not be pulled. Please ensure the image exists locally or is available in a registry.")
                print(f"✅ Docker image '{docker_image}' pulled successfully.")
            
            # Build default image if necessary (only for default image, not custom ones)
            if docker_image == self.docker_image:
                self.build_image()
            
            # Validate that the main program file exists
            # Skip validation for custom Docker images since the code is inside the image
            if docker_image == self.docker_image:
                if not self._validate_program_files(full_host_path, main_file_name):
                    # Try to validate using the container path
                    container_path = Path("/project") / program_path
                    if not self._validate_program_files(container_path, main_file_name):
                        raise Exception(f"Main program file '{main_file_name}' not found in {full_host_path} or {container_path}. Please ensure the file exists or update the configuration.")
                    else:
                        print(f"✅ Found main file in container path: {container_path}")
            else:
                print(f"✅ Skipping file validation for custom Docker image: {docker_image}")
            
            # Get timeout from config
            config = self.load_config()
            timeout = config.get("settings", {}).get("timeout_seconds", 300)
            
            # Log execution details for better tracking
            print(f"🔍 Execution details:")
            print(f"   - Program ID: {program_id}")
            print(f"   - Execution ID: {execution_id}")
            print(f"   - Docker Image: {docker_image}")
            print(f"   - Main File: {main_file_name}")
            print(f"   - Host Path: {full_host_path}")
            print(f"   - Timeout: {timeout}s")
            print(f"   - Concurrent Executions: {len([e for e in executions.values() if e.status == 'running'])}")
            
            # Check concurrent execution limits
            max_concurrent = config.get("settings", {}).get("max_concurrent_executions", 5)
            current_concurrent = len([e for e in executions.values() if e.status == 'running'])
            
            if current_concurrent >= max_concurrent:
                raise Exception(f"Maximum concurrent executions ({max_concurrent}) reached. Please wait for some executions to complete.")
            
            print(f"✅ Concurrent execution check passed ({current_concurrent}/{max_concurrent})")
            
            # Prepare Docker command using absolute host path
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{str(full_host_path)}:/workspace"
            ]
            
            # Check if this is a custom Docker image (not the default one)
            is_custom_image = docker_image != self.docker_image
            
            if is_custom_image:
                # For custom Docker images, use --env-file approach
                # The .env file is in the host directory that gets mounted to /workspace
                # Since we're running docker from inside the container, we need to use the host path
                # The host path is mounted at /project in the container
                env_file_path = Path("/project") / program_path / ".env"
                if env_file_path.exists():
                    print(f"📄 Using --env-file for custom image: {env_file_path}")
                    docker_cmd.extend(["--env-file", str(env_file_path)])
                else:
                    print(f"⚠️ No .env file found at {env_file_path} for custom image")
                    # Try to use the host path directly since we're running docker from host context
                    host_env_path = str(full_host_path) + "/.env"
                    print(f"📄 Trying host path for .env: {host_env_path}")
                    docker_cmd.extend(["--env-file", host_env_path])
            else:
                # For default image, use individual environment variables (current behavior)
                env_vars = self.get_env_vars(full_host_path)
                for key, value in env_vars.items():
                    docker_cmd.extend(["-e", f"{key}={value}"])
            
            # Add environment variables for actions (always needed)
            docker_cmd.extend(["-e", f"PROGRAM_ID={program_id}"])
            docker_cmd.extend(["-e", f"EXECUTION_ID={execution_id}"])
            
            # Add parameters as environment variables (always needed)
            if parameters:
                for key, value in parameters.items():
                    docker_cmd.extend(["-e", f"PARAM_{key.upper()}={value}"])
            
            docker_cmd.extend([docker_image])
            
            # For custom Docker images, use the default CMD from the image
            # For default images, build a specific command to execute the main file
            if docker_image == self.docker_image:
                # Get parameters from program configuration
                program_parameters = program_config.get("parameters", "")
                
                # Log parameters if they exist
                if program_parameters:
                    print(f"📋 Program parameters: {program_parameters}")
                else:
                    print(f"📋 No parameters configured for this program")
                
                # Build container command for default image
                container_cmd = self._build_container_command(full_host_path, main_file_name, program_parameters)
                
                # For Node.js files, use a simpler approach
                if main_file_name.endswith('.js'):
                    if program_parameters:
                        docker_cmd.extend(["node", f"/workspace/{main_file_name}", *program_parameters.split()])
                    else:
                        docker_cmd.extend(["node", f"/workspace/{main_file_name}"])
                else:
                    docker_cmd.extend(["/bin/sh", "-c", container_cmd])
            else:
                # For custom Docker images, use the default CMD from the image
                print(f"🐳 Using default CMD from custom Docker image: {docker_image}")
                # No additional command needed - Docker will use the image's default CMD
            
            print(f"�� Docker command: {' '.join(docker_cmd)}")
            print(f"🐳 Docker command to run: {docker_cmd}")
            
            # Log execution start
            print(f"🚀 Starting Docker execution for {program_id}")
            print(f"   - Container will run: {docker_image}")
            print(f"   - Working directory: /workspace")
            print(f"   - Main file: {main_file_name}")
            
            # Execute container from host in a separate thread to avoid blocking the event loop
            def run_docker_command():
                print(f"🔧 Executing Docker command for {program_id}...")
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                print(f"🏁 Docker execution completed for {program_id} with exit code: {result.returncode}")
                return result
            
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
            print(f"❌ Error executing program {program_id}: {str(e)}")
    
    def _build_container_command(self, program_path: Path, main_file_name: str, parameters: str = "") -> str:
        """Build the command to execute inside the container"""
        commands = []
        
        # Change to working directory
        commands.append("cd /workspace")
        
        # Install dependencies if requirements.txt exists (only for Python images)
        commands.append("if command -v pip >/dev/null 2>&1 && [ -f requirements.txt ]; then pip install -r requirements.txt; fi")
        
        # Execute action BEFORE the program (only for Python images)
        commands.append("if command -v python >/dev/null 2>&1 && [ -f /project/actions/act_before.py ]; then python /project/actions/act_before.py; fi")
        
        # Execute the main program and capture exit code
        # Support different interpreters based on file extension
        if main_file_name.endswith('.py'):
            if parameters:
                commands.append(f"python {main_file_name} {parameters}")
            else:
                commands.append(f"python {main_file_name}")
        elif main_file_name.endswith('.js'):
            if parameters:
                commands.append(f"node {main_file_name} {parameters}")
            else:
                commands.append(f"node {main_file_name}")
        elif main_file_name.endswith('.sh'):
            if parameters:
                commands.append(f"bash {main_file_name} {parameters}")
            else:
                commands.append(f"bash {main_file_name}")
        else:
            # Default to python for unknown extensions
            if parameters:
                commands.append(f"python {main_file_name} {parameters}")
            else:
                commands.append(f"python {main_file_name}")
        
        commands.append("EXIT_CODE=$?")
        commands.append("export EXIT_CODE")
        
        # Execute action AFTER the program (only for Python images)
        commands.append("if command -v python >/dev/null 2>&1 && [ -f /project/actions/act_after.py ]; then python /project/actions/act_after.py; fi")
        
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
    
    async def _validate_docker_image(self, image_name: str) -> bool:
        """Check if a Docker image exists locally"""
        try:
            def check_image():
                result = subprocess.run(
                    ["docker", "images", "-q", image_name],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0 and result.stdout.strip() != ""
            
            return await asyncio.to_thread(check_image)
        except Exception as e:
            print(f"⚠️ Error checking Docker image '{image_name}': {str(e)}")
            return False
    
    async def _pull_docker_image(self, image_name: str) -> bool:
        """Try to pull a Docker image from registry"""
        try:
            print(f"📥 Attempting to pull Docker image: {image_name}")
            def pull_image():
                result = subprocess.run(
                    ["docker", "pull", image_name],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                return result.returncode == 0
            
            success = await asyncio.to_thread(pull_image)
            if success:
                print(f"✅ Successfully pulled Docker image: {image_name}")
            else:
                print(f"❌ Failed to pull Docker image: {image_name}")
            return success
        except Exception as e:
            print(f"❌ Error pulling Docker image '{image_name}': {str(e)}")
            return False
    
    def _validate_program_files(self, program_path: Path, main_file_name: str) -> bool:
        """Validate that the main program file exists"""
        main_file_path = program_path / main_file_name
        if not main_file_path.exists():
            # Try alternative files
            alternative_files = ["main.py", "run.py", "app.py", "index.py"]
            for alt_file in alternative_files:
                alt_path = program_path / alt_file
                if alt_path.exists():
                    print(f"📄 Found alternative file: {alt_file} instead of {main_file_name}")
                    return True
            return False
        return True
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """Dependency to get current authenticated user"""
        token = credentials.credentials
        username = self.verify_token(token)
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    
    def setup_routes(self):
        """Setup API routes"""
        
        # Generate random credentials at startup
        global auth_credentials
        if auth_credentials is None:
            auth_credentials = self.generate_random_credentials()
            print("\n" + "=" * 60)
            print("🔐 CREDENCIALES DE USO")
            print("=" * 60)
            print(f"👤 Usuario: {auth_credentials.username}")
            print(f"🔑 Password: {auth_credentials.password}")
            print("=" * 60)
            print("💡 Usa estas credenciales para hacer login en /auth/login")
            print("🔒 Las credenciales solo se muestran una vez por seguridad")
            print("=" * 60 + "\n")
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint"""
            return {
                "message": "Serverless Docker API",
                "version": "1.0.0",
                "status": "running",
                "container": "docker"
            }
        
        @self.app.post("/auth/login", response_model=LoginResponse)
        async def login(request: LoginRequest):
            """Login with username and password to get access token"""
            # Check if credentials match
            if (request.username != auth_credentials.username or 
                not self.verify_password(request.password, self.get_password_hash(auth_credentials.password))):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": request.username}, expires_delta=access_token_expires
            )
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
                username=request.username
            )
        
        
        @self.app.get("/health", response_model=Dict[str, str])
        async def health_check():
            """API health check"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/programs", response_model=List[ProgramInfo])
        async def list_programs(current_user: str = Depends(self.get_current_user)):
            """List all available programs"""
            print("🔍 /programs endpoint called")
            config = self.load_config()
            print(f"📋 Config loaded with {len(config.get('scripts', {}))} scripts and {len(config.get('bots', {}))} bots")
            programs = []
            
            # Add scripts
            for script_id, script_config in config.get("scripts", {}).items():
                if script_config.get("enabled", True):
                    programs.append(ProgramInfo(
                        id=script_config.get("id", script_id),
                        name=script_config.get("name", script_id),
                        type="script",
                        description=script_config.get("description", ""),
                        enabled=script_config.get("enabled", True),
                        path=script_config.get("path", ""),
                        key=script_id,
                        docker_image=script_config.get("docker_image"),
                        parameters=script_config.get("parameters")
                    ))
            
            # Add bots
            for bot_id, bot_config in config.get("bots", {}).items():
                if bot_config.get("enabled", True):
                    programs.append(ProgramInfo(
                        id=bot_config.get("id", bot_id),
                        name=bot_config.get("name", bot_id),
                        type="bot",
                        description=bot_config.get("description", ""),
                        enabled=bot_config.get("enabled", True),
                        path=bot_config.get("path", ""),
                        key=bot_id,
                        docker_image=bot_config.get("docker_image"),
                        parameters=bot_config.get("parameters")
                    ))
            
            return programs
        
        @self.app.get("/test", response_model=Dict[str, str])
        async def test_endpoint():
            """Test endpoint to verify basic functionality"""
            print("🧪 Test endpoint called")
            return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/execute", response_model=ExecutionResponse)
        async def execute_program(request: ExecutionRequest, background_tasks: BackgroundTasks, current_user: str = Depends(self.get_current_user)):
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
        async def list_executions(current_user: str = Depends(self.get_current_user)):
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
        async def get_executions_stats(current_user: str = Depends(self.get_current_user)):
            """Get execution statistics with detailed program breakdown"""
            if not executions:
                return {
                    "total": 0,
                    "by_status": {
                        "completed": [],
                        "failed": [],
                        "timeout": [],
                        "running": [],
                        "queued": []
                    },
                    "recent_executions": 0,
                    "max_executions": MAX_EXECUTIONS,
                    "concurrent_executions": 0
                }
            
            # Count by status and program
            status_program_counts = {}
            for execution in executions.values():
                status = execution.status
                program_id = execution.program_id
                
                if status not in status_program_counts:
                    status_program_counts[status] = {}
                
                if program_id not in status_program_counts[status]:
                    status_program_counts[status][program_id] = 0
                
                status_program_counts[status][program_id] += 1
            
            # Convert to the requested format
            by_status = {}
            for status in ["completed", "failed", "timeout", "running", "queued"]:
                by_status[status] = []
                if status in status_program_counts:
                    for program_id, count in status_program_counts[status].items():
                        by_status[status].append({
                            "name": program_id,
                            "total": count
                        })
                    # Sort by count (descending) then by name
                    by_status[status].sort(key=lambda x: (-x["total"], x["name"]))
            
            # Count recent executions (last 24 hours)
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_count = sum(
                1 for execution in executions.values()
                if execution.start_time and execution.start_time > cutoff_time
            )
            
            # Count concurrent executions
            concurrent_count = len([e for e in executions.values() if e.status == 'running'])
            
            return {
                "total": len(executions),
                "by_status": by_status,
                "recent_executions": recent_count,
                "max_executions": MAX_EXECUTIONS,
                "concurrent_executions": concurrent_count
            }
        
        @self.app.get("/executions/concurrent", response_model=Dict[str, Any])
        async def get_concurrent_executions():
            """Get information about currently running executions"""
            config = self.load_config() # Load config here to get max_concurrent_executions
            running_executions = [
                {
                    "execution_id": exec_id,
                    "program_id": exec_status.program_id,
                    "start_time": exec_status.start_time.isoformat() if exec_status.start_time else None,
                    "duration_seconds": (datetime.now() - exec_status.start_time).total_seconds() if exec_status.start_time else None
                }
                for exec_id, exec_status in executions.items()
                if exec_status.status == 'running'
            ]
            
            return {
                "concurrent_count": len(running_executions),
                "max_concurrent": config.get("settings", {}).get("max_concurrent_executions", 5),
                "running_executions": running_executions
            }
        
        @self.app.delete("/executions/cleanup")
        async def cleanup_executions():
            """Manually clean all finished executions"""
            return await self.manual_cleanup_executions()
        
        @self.app.get("/executions/{execution_id}", response_model=ExecutionStatus)
        async def get_execution_status(execution_id: str, current_user: str = Depends(self.get_current_user)):
            """Get execution status"""
            if execution_id not in executions:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            return executions[execution_id]
        
        @self.app.get("/executions/{execution_id}/logs", response_model=Dict[str, Any])
        async def get_execution_logs(execution_id: str, current_user: str = Depends(self.get_current_user)):
            """Get execution logs with additional details"""
            if execution_id not in executions:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            execution = executions[execution_id]
            
            # Calculate duration if execution has started
            duration = None
            if execution.start_time:
                end_time = execution.end_time or datetime.now()
                duration = (end_time - execution.start_time).total_seconds()
            
            return {
                "execution_id": execution_id,
                "program_id": execution.program_id,
                "status": execution.status,
                "start_time": execution.start_time.isoformat() if execution.start_time else None,
                "end_time": execution.end_time.isoformat() if execution.end_time else None,
                "duration_seconds": duration,
                "output": execution.output,
                "error": execution.error,
                "output_lines": len(execution.output.split('\n')) if execution.output else 0,
                "error_lines": len(execution.error.split('\n')) if execution.error else 0
            }
        
        @self.app.get("/containers/logs/{image_name}", response_model=Dict[str, Any])
        async def get_container_logs_by_image(image_name: str):
            """Get logs from all containers running a specific Docker image"""
            try:
                # Get running containers with the specified image
                def get_containers():
                    result = subprocess.run(
                        ["docker", "ps", "--filter", f"ancestor={image_name}", "--format", "{{.ID}}"],
                        capture_output=True,
                        text=True
                    )
                    return result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                container_ids = await asyncio.to_thread(get_containers)
                
                if not container_ids:
                    return {
                        "image_name": image_name,
                        "message": f"No running containers found for image: {image_name}",
                        "containers": [],
                        "total_containers": 0
                    }
                
                # Get logs for each container
                container_logs = []
                for container_id in container_ids:
                    if container_id:  # Skip empty lines
                        def get_container_logs(cid):
                            result = subprocess.run(
                                ["docker", "logs", "--tail", "100", cid],
                                capture_output=True,
                                text=True
                            )
                            return {
                                "container_id": cid,
                                "stdout": result.stdout,
                                "stderr": result.stderr,
                                "logs_lines": len(result.stdout.split('\n')) + len(result.stderr.split('\n'))
                            }
                        
                        logs = await asyncio.to_thread(get_container_logs, container_id)
                        container_logs.append(logs)
                
                return {
                    "image_name": image_name,
                    "containers": container_logs,
                    "total_containers": len(container_logs),
                    "message": f"Found {len(container_logs)} running containers for image: {image_name}"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error getting container logs: {str(e)}")
        
        @self.app.get("/containers/active", response_model=Dict[str, Any])
        async def get_active_containers():
            """Get all active containers with their images and basic info"""
            try:
                def get_active_containers_info():
                    result = subprocess.run(
                        ["docker", "ps", "--format", "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"],
                        capture_output=True,
                        text=True
                    )
                    return result.stdout.strip().split('\n')[1:] if result.stdout.strip() else []  # Skip header
                
                containers_info = await asyncio.to_thread(get_active_containers_info)
                
                containers = []
                for line in containers_info:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 4:
                            containers.append({
                                "container_id": parts[0],
                                "image": parts[1],
                                "status": parts[2],
                                "name": parts[3]
                            })
                
                return {
                    "total_containers": len(containers),
                    "containers": containers
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error getting active containers: {str(e)}")
        
        @self.app.get("/images/available", response_model=Dict[str, Any])
        async def get_available_images():
            """Get all available Docker images from configuration"""
            try:
                config = self.load_config()
                images = []
                
                # Get images from scripts
                for script_id, script_config in config.get("scripts", {}).items():
                    if script_config.get("enabled", True):
                        docker_image = script_config.get("docker_image")
                        if docker_image:
                            images.append({
                                "repository": docker_image.split(':')[0] if ':' in docker_image else docker_image,
                                "tag": docker_image.split(':')[1] if ':' in docker_image else "latest",
                                "image_id": "config",
                                "size": "N/A",
                                "created_at": "N/A",
                                "full_name": docker_image,
                                "source": "script",
                                "script_id": script_id
                            })
                
                # Get images from bots
                for bot_id, bot_config in config.get("bots", {}).items():
                    if bot_config.get("enabled", True):
                        docker_image = bot_config.get("docker_image")
                        if docker_image:
                            images.append({
                                "repository": docker_image.split(':')[0] if ':' in docker_image else docker_image,
                                "tag": docker_image.split(':')[1] if ':' in docker_image else "latest",
                                "image_id": "config",
                                "size": "N/A",
                                "created_at": "N/A",
                                "full_name": docker_image,
                                "source": "bot",
                                "bot_id": bot_id
                            })
                
                # Add default image from settings
                default_image = config.get("settings", {}).get("docker_image", "pyexecutorhub-base")
                if default_image:
                    images.append({
                        "repository": default_image.split(':')[0] if ':' in default_image else default_image,
                        "tag": default_image.split(':')[1] if ':' in default_image else "latest",
                        "image_id": "config",
                        "size": "N/A",
                        "created_at": "N/A",
                        "full_name": default_image,
                        "source": "default",
                        "description": "Default image for programs without custom image"
                    })
                
                return {
                    "total_images": len(images),
                    "images": images
                }
                
            except Exception as e:
                print(f"❌ Error in get_available_images: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error getting available images: {str(e)}")
        
        @self.app.get("/images/search/{image_name}", response_model=Dict[str, Any])
        async def search_images(image_name: str):
            """Search for specific Docker images in configuration"""
            try:
                config = self.load_config()
                images = []
                
                # Search in scripts
                for script_id, script_config in config.get("scripts", {}).items():
                    if script_config.get("enabled", True):
                        docker_image = script_config.get("docker_image")
                        if docker_image and image_name.lower() in docker_image.lower():
                            images.append({
                                "repository": docker_image.split(':')[0] if ':' in docker_image else docker_image,
                                "tag": docker_image.split(':')[1] if ':' in docker_image else "latest",
                                "image_id": "config",
                                "size": "N/A",
                                "created_at": "N/A",
                                "full_name": docker_image,
                                "source": "script",
                                "script_id": script_id
                            })
                
                # Search in bots
                for bot_id, bot_config in config.get("bots", {}).items():
                    if bot_config.get("enabled", True):
                        docker_image = bot_config.get("docker_image")
                        if docker_image and image_name.lower() in docker_image.lower():
                            images.append({
                                "repository": docker_image.split(':')[0] if ':' in docker_image else docker_image,
                                "tag": docker_image.split(':')[1] if ':' in docker_image else "latest",
                                "image_id": "config",
                                "size": "N/A",
                                "created_at": "N/A",
                                "full_name": docker_image,
                                "source": "bot",
                                "bot_id": bot_id
                            })
                
                # Search in default image
                default_image = config.get("settings", {}).get("docker_image", "pyexecutorhub-base")
                if default_image and image_name.lower() in default_image.lower():
                    images.append({
                        "repository": default_image.split(':')[0] if ':' in default_image else default_image,
                        "tag": default_image.split(':')[1] if ':' in default_image else "latest",
                        "image_id": "config",
                        "size": "N/A",
                        "created_at": "N/A",
                        "full_name": default_image,
                        "source": "default",
                        "description": "Default image for programs without custom image"
                    })
                
                return {
                    "search_term": image_name,
                    "total_images": len(images),
                    "images": images
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error searching images: {str(e)}")

# Create API instance
api = ServerlessAPI()
app = api.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 