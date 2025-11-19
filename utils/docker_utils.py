"""Docker utilities"""
import asyncio
import subprocess
from pathlib import Path
from typing import Dict


class DockerUtils:
    """Utility class for Docker operations"""
    
    @staticmethod
    async def validate_docker_image(image_name: str) -> bool:
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
    
    @staticmethod
    async def pull_docker_image(image_name: str) -> bool:
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
    
    @staticmethod
    def build_image(docker_image: str, project_dir: str = "/project"):
        """Build the base Docker image if it doesn't exist"""
        try:
            result = subprocess.run(
                ["docker", "images", "-q", docker_image],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                print(f"🔨 Building Docker image: {docker_image}")
                print(f"📁 Building from: {project_dir}")
                subprocess.run(
                    ["docker", "build", "-t", docker_image, project_dir],
                    check=True
                )
                print("✅ Image built successfully")
            else:
                print(f"✅ Image {docker_image} already exists")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building Docker image: {e}")
            raise Exception(f"Error building Docker image: {e}")
    
    @staticmethod
    def validate_program_files(program_path: Path, main_file_name: str) -> bool:
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

