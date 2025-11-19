"""Container routes"""
import asyncio
import subprocess
from typing import Any, Dict
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/containers", tags=["containers"])


@router.get("/logs/{image_name}", response_model=Dict[str, Any])
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


@router.get("/active", response_model=Dict[str, Any])
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

