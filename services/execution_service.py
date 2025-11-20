"""Execution service"""
import asyncio
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import dotenv_values

from models.execution_models import ExecutionStatus
from services.config_service import ConfigService
from services.execution_storage import ExecutionStorage
from utils.docker_utils import DockerUtils
from utils.log_formatter import format_logs


class ExecutionService:
    """Service for executing programs"""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self.docker_utils = DockerUtils()
        self.storage = ExecutionStorage()
    
    def get_env_vars(self, program_path: Path) -> Dict[str, str]:
        """Read environment variables from the program's .env file"""
        env_file = program_path / ".env"
        if env_file.exists():
            print(f"📄 Loading environment variables from: {env_file}")
            return dotenv_values(env_file)
        return {}
    
    def _parse_parameters_string(self, params_str: str) -> Dict[str, Any]:
        """Parse command-line parameters string into dictionary
        
        Examples:
            "--process 19" -> {"process": "19"}
            "--process 19 --verbose" -> {"process": "19", "verbose": True}
            "--host api.example.com --port 8080" -> {"host": "api.example.com", "port": "8080"}
        """
        if not params_str or not params_str.strip():
            return {}
        
        params_dict = {}
        parts = params_str.split()
        i = 0
        while i < len(parts):
            arg = parts[i]
            if arg.startswith('--'):
                # Remove '--' prefix
                key = arg[2:]
                # Check if next part is a value (not another flag)
                if i + 1 < len(parts) and not parts[i + 1].startswith('--'):
                    params_dict[key] = parts[i + 1]
                    i += 2
                else:
                    # Boolean flag (no value)
                    params_dict[key] = True
                    i += 1
            else:
                i += 1
        
        return params_dict
    
    
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
    
    async def execute_program(self, execution_id: str, program_id: str, parameters: Dict = None):
        """Execute a program in background"""
        try:
            # Update status
            self.storage.add_execution(ExecutionStatus(
                execution_id=execution_id,
                program_id=program_id,
                status="running",
                start_time=datetime.now()
            ))
            
            # Get program configuration
            program_config = self.config_service.get_program_by_id(program_id)
            if not program_config:
                raise Exception(f"Program with ID '{program_id}' not found")
            
            if not program_config.get("enabled", True):
                raise Exception(f"Program '{program_id}' is disabled")
            
            # Check if this program uses docker compose execution
            docker_compose_path = program_config.get("path_docker_compose_run")
            if docker_compose_path:
                # Execute using docker compose
                await self._execute_docker_compose(execution_id, program_id, program_config, docker_compose_path, parameters)
                return
            
            # Use absolute host path for volume mounting
            host_project_dir = os.getenv("HOST_PROJECT_DIR", "/app")
            program_path = Path(program_config["path"])
            full_host_path = Path(host_project_dir) / program_path
            print(f"Mounting volume: {str(full_host_path)}:/workspace")
            
            # Use main_file from configuration or default to main.py
            main_file_name = program_config.get("main_file", "main.py")
            
            print(f"🚀 Executing program: {program_id} ({program_path}) with file: {main_file_name}")
            
            # Determine which Docker image to use
            docker_image = program_config.get("docker_image", self.config_service.docker_image)
            print(f"🐳 Using Docker image: {docker_image}")
            
            # Validate that the Docker image exists (optional check)
            if not await self.docker_utils.validate_docker_image(docker_image):
                print(f"⚠️ Warning: Docker image '{docker_image}' may not exist. Attempting to pull...")
                if not await self.docker_utils.pull_docker_image(docker_image):
                    raise Exception(f"Docker image '{docker_image}' not found and could not be pulled. Please ensure the image exists locally or is available in a registry.")
                print(f"✅ Docker image '{docker_image}' pulled successfully.")
            
            # Build default image if necessary (only for default image, not custom ones)
            if docker_image == self.config_service.docker_image:
                self.docker_utils.build_image(docker_image)
            
            # Validate that the main program file exists
            if docker_image == self.config_service.docker_image:
                if not self.docker_utils.validate_program_files(full_host_path, main_file_name):
                    container_path = Path("/project") / program_path
                    if not self.docker_utils.validate_program_files(container_path, main_file_name):
                        raise Exception(f"Main program file '{main_file_name}' not found in {full_host_path} or {container_path}. Please ensure the file exists or update the configuration.")
                    else:
                        print(f"✅ Found main file in container path: {container_path}")
            else:
                print(f"✅ Skipping file validation for custom Docker image: {docker_image}")
            
            # Get timeout from config
            config = self.config_service.load_config()
            timeout = config.get("settings", {}).get("timeout_seconds", 300)
            
            # Log execution details
            print(f"🔍 Execution details:")
            print(f"   - Program ID: {program_id}")
            print(f"   - Execution ID: {execution_id}")
            print(f"   - Docker Image: {docker_image}")
            print(f"   - Main File: {main_file_name}")
            print(f"   - Host Path: {full_host_path}")
            print(f"   - Timeout: {timeout}s")
            
            executions = self.storage.get_executions()
            current_concurrent = len([e for e in executions.values() if e.status == 'running'])
            print(f"   - Concurrent Executions: {current_concurrent}")
            
            # Check concurrent execution limits
            max_concurrent = config.get("settings", {}).get("max_concurrent_executions", 5)
            if current_concurrent >= max_concurrent:
                raise Exception(f"Maximum concurrent executions ({max_concurrent}) reached. Please wait for some executions to complete.")
            
            print(f"✅ Concurrent execution check passed ({current_concurrent}/{max_concurrent})")
            
            # Prepare Docker command
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{str(full_host_path)}:/workspace"
            ]
            
            # Check if this is a custom Docker image
            is_custom_image = docker_image != self.config_service.docker_image
            
            if is_custom_image:
                # For custom Docker images, use --env-file approach
                env_file_path = Path("/project") / program_path / ".env"
                if env_file_path.exists():
                    print(f"📄 Using --env-file for custom image: {env_file_path}")
                    docker_cmd.extend(["--env-file", str(env_file_path)])
                else:
                    print(f"⚠️ No .env file found at {env_file_path} for custom image")
                    host_env_path = str(full_host_path) + "/.env"
                    print(f"📄 Trying host path for .env: {host_env_path}")
                    docker_cmd.extend(["--env-file", host_env_path])
            else:
                # For default image, use individual environment variables
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
            if docker_image == self.config_service.docker_image:
                # Get parameters from program configuration
                program_parameters = program_config.get("parameters", "")
                
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
                # For custom Docker images, pass parameters if configured
                program_parameters = program_config.get("parameters", "")
                if program_parameters:
                    print(f"🐳 Using custom Docker image with parameters: {docker_image}")
                    print(f"📋 Program parameters: {program_parameters}")
                    docker_cmd.extend(program_parameters.split())
                else:
                    print(f"🐳 Using default CMD from custom Docker image: {docker_image}")
            
            print(f"🐳 Docker command: {' '.join(docker_cmd)}")
            print(f"🐳 Docker command to run: {docker_cmd}")
            
            # Log execution start
            print(f"🚀 Starting Docker execution for {program_id}")
            print(f"   - Container will run: {docker_image}")
            print(f"   - Working directory: /workspace")
            print(f"   - Main file: {main_file_name}")
            
            # Execute container from host in a separate thread
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
            self.storage.update_execution(
                execution_id,
                end_time=datetime.now(),
                output=format_logs(result.stdout),
                error=format_logs(result.stderr)
            )
            
            if result.returncode == 0:
                self.storage.update_execution(execution_id, status="completed")
                print(f"✅ Program {program_id} executed successfully")
            else:
                self.storage.update_execution(execution_id, status="failed")
                print(f"❌ Program {program_id} failed with code {result.returncode}")
            
        except subprocess.TimeoutExpired:
            self.storage.update_execution(
                execution_id,
                status="timeout",
                end_time=datetime.now(),
                error="Execution exceeded time limit"
            )
            print(f"⏰ Program {program_id} exceeded time limit")
            
        except Exception as e:
            self.storage.update_execution(
                execution_id,
                status="failed",
                end_time=datetime.now(),
                error=str(e)
            )
            print(f"❌ Error executing program {program_id}: {str(e)}")
    
    async def _execute_docker_compose(self, execution_id: str, program_id: str, program_config: Dict, docker_compose_path: str, parameters: Dict = None):
        """Execute program using docker compose up"""
        try:
            # Get timeout from config
            config = self.config_service.load_config()
            timeout = config.get("settings", {}).get("timeout_seconds", 300)
            
            # Resolve docker compose file path
            host_project_dir = os.getenv("HOST_PROJECT_DIR", "/app")
            program_path = Path(program_config["path"])
            
            # docker_compose_path can be relative to program_path or absolute
            # Check if it starts with / to determine if it's absolute
            if docker_compose_path.startswith('/'):
                # Absolute path - use as is
                compose_file_path = Path(docker_compose_path)
            else:
                # Relative path - resolve relative to program_path
                # First try relative to host_project_dir/program_path
                compose_file_path = Path(host_project_dir) / program_path / docker_compose_path
            
            compose_dir = compose_file_path.parent
            
            print(f"🐳 Using Docker Compose execution for {program_id}")
            print(f"   - Compose file: {compose_file_path}")
            print(f"   - Working directory: {compose_dir}")
            print(f"   - Timeout: {timeout}s")
            
            # Check if compose file exists
            if not compose_file_path.exists():
                raise Exception(f"Docker Compose file not found: {compose_file_path}")
            
            # Build docker compose command
            # Use 'docker compose' (Docker Compose V2)
            # NOTA: Para docker compose, los parámetros deben estar definidos directamente
            # en el docker-compose.yml. Si necesitas diferentes parámetros, crea archivos
            # docker-compose.yml separados (ej: docker-compose-19.yml, docker-compose-20.yml)
            compose_cmd_base = ["docker", "compose", "-f", str(compose_file_path)]
            
            # Check concurrent execution limits
            executions = self.storage.get_executions()
            current_concurrent = len([e for e in executions.values() if e.status == 'running'])
            max_concurrent = config.get("settings", {}).get("max_concurrent_executions", 5)
            
            if current_concurrent >= max_concurrent:
                raise Exception(f"Maximum concurrent executions ({max_concurrent}) reached. Please wait for some executions to complete.")
            
            print(f"✅ Concurrent execution check passed ({current_concurrent}/{max_concurrent})")
            
            # Prepare environment variables for docker compose
            # Para docker compose, NO se parsean parámetros del config.yaml
            # Se espera que cada configuración tenga su propio docker-compose.yml
            # con los parámetros ya definidos directamente en el archivo
            compose_env = os.environ.copy()
            compose_env["PROGRAM_ID"] = program_id
            compose_env["EXECUTION_ID"] = execution_id
            
            print(f"📋 Nota: Para docker compose, los parámetros deben estar definidos directamente en el docker-compose.yml")
            print(f"   Si necesitas diferentes parámetros, crea archivos docker-compose separados")
            print(f"   (ej: docker-compose-19.yml, docker-compose-20.yml, etc.)")
            
            # Execute docker compose up
            def run_docker_compose():
                print(f"🔧 Executing docker compose up for {program_id}...")
                print(f"📂 Working directory: {compose_dir}")
                print(f"📄 Using compose file: {compose_file_path}")
                
                # Change to compose file directory and run docker compose up
                result = subprocess.run(
                    compose_cmd_base + ["up", "--remove-orphans"],
                    cwd=str(compose_dir),
                    env=compose_env,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                # Always run docker compose down to clean up
                print(f"🧹 Cleaning up docker compose services for {program_id}...")
                cleanup_result = subprocess.run(
                    compose_cmd_base + ["down", "--remove-orphans"],
                    cwd=str(compose_dir),
                    capture_output=True,
                    text=True,
                    timeout=60  # Shorter timeout for cleanup
                )
                
                if cleanup_result.returncode != 0:
                    print(f"⚠️ Warning: Docker compose down failed: {cleanup_result.stderr}")
                
                print(f"🏁 Docker compose execution completed for {program_id} with exit code: {result.returncode}")
                return result
            
            result = await asyncio.to_thread(run_docker_compose)
            
            # Update final status with properly formatted logs
            self.storage.update_execution(
                execution_id,
                end_time=datetime.now(),
                output=format_logs(result.stdout),
                error=format_logs(result.stderr)
            )
            
            if result.returncode == 0:
                self.storage.update_execution(execution_id, status="completed")
                print(f"✅ Program {program_id} executed successfully with docker compose")
            else:
                self.storage.update_execution(execution_id, status="failed")
                print(f"❌ Program {program_id} failed with docker compose (exit code: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            # Try to cleanup even on timeout
            try:
                # Re-resolve compose file path for cleanup
                if docker_compose_path.startswith('/'):
                    compose_file_path = Path(docker_compose_path)
                else:
                    compose_file_path = Path(host_project_dir) / program_path / docker_compose_path
                compose_dir = compose_file_path.parent
                compose_cmd_base = ["docker", "compose", "-f", str(compose_file_path)]
                subprocess.run(
                    compose_cmd_base + ["down", "--remove-orphans"],
                    cwd=str(compose_dir),
                    timeout=30
                )
            except Exception as cleanup_error:
                print(f"⚠️ Warning: Failed to cleanup docker compose on timeout: {cleanup_error}")
            
            self.storage.update_execution(
                execution_id,
                status="timeout",
                end_time=datetime.now(),
                error="Execution exceeded time limit"
            )
            print(f"⏰ Program {program_id} exceeded time limit")
            
        except Exception as e:
            self.storage.update_execution(
                execution_id,
                status="failed",
                end_time=datetime.now(),
                error=str(e)
            )
            print(f"❌ Error executing program {program_id} with docker compose: {str(e)}")

