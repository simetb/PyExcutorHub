"""Program models"""
from typing import Optional
from pydantic import BaseModel


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
    path_docker_compose_run: Optional[str] = None  # Path to docker-compose file for docker compose up execution

