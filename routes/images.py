"""Image routes"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends

from services.config_service import ConfigService

router = APIRouter(prefix="/images", tags=["images"])

# Global config service instance (will be set by main app)
_config_service: Optional[ConfigService] = None


def set_config_service(config_service: ConfigService):
    """Set the config service instance"""
    global _config_service
    _config_service = config_service


def get_config_service() -> ConfigService:
    """Dependency to get config service"""
    if _config_service is None:
        raise HTTPException(status_code=500, detail="Config service not initialized")
    return _config_service


@router.get("/available", response_model=Dict[str, Any])
async def get_available_images(
    config_service: ConfigService = Depends(get_config_service)
):
    """Get all available Docker images from configuration"""
    try:
        config = config_service.load_config()
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


@router.get("/search/{image_name}", response_model=Dict[str, Any])
async def search_images(
    image_name: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Search for specific Docker images in configuration"""
    try:
        config = config_service.load_config()
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

