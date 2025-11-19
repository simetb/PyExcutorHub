"""Program routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from models.program_models import ProgramInfo
from routes.auth import get_current_user
from services.config_service import ConfigService

router = APIRouter(prefix="/programs", tags=["programs"])

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


@router.get("", response_model=List[ProgramInfo])
async def list_programs(
    current_user: str = Depends(get_current_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """List all available programs"""
    print("🔍 /programs endpoint called")
    config = config_service.load_config()
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
                parameters=script_config.get("parameters"),
                path_docker_compose_run=script_config.get("path_docker_compose_run")
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
                parameters=bot_config.get("parameters"),
                path_docker_compose_run=bot_config.get("path_docker_compose_run")
            ))
    
    return programs

