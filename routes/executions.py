"""Execution routes"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from models.execution_models import ExecutionRequest, ExecutionResponse, ExecutionStatus
from routes.auth import get_current_user
from services.config_service import ConfigService
from services.execution_service import ExecutionService
from services.execution_storage import ExecutionStorage

router = APIRouter(prefix="/executions", tags=["executions"])

# Global service instances (will be set by main app)
_config_service: Optional[ConfigService] = None
_execution_service: Optional[ExecutionService] = None


def set_config_service(config_service: ConfigService):
    """Set the config service instance"""
    global _config_service
    _config_service = config_service


def set_execution_service(execution_service: ExecutionService):
    """Set the execution service instance"""
    global _execution_service
    _execution_service = execution_service


def get_config_service() -> ConfigService:
    """Dependency to get config service"""
    if _config_service is None:
        raise HTTPException(status_code=500, detail="Config service not initialized")
    return _config_service


def get_execution_service() -> ExecutionService:
    """Dependency to get execution service"""
    if _execution_service is None:
        raise HTTPException(status_code=500, detail="Execution service not initialized")
    return _execution_service


def get_execution_storage() -> ExecutionStorage:
    """Dependency to get execution storage"""
    return ExecutionStorage()


@router.post("", response_model=ExecutionResponse)
async def execute_program(
    request: ExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    config_service: ConfigService = Depends(get_config_service),
    execution_service: ExecutionService = Depends(get_execution_service)
):
    """Execute a program"""
    print(f"🔍 Starting execution for program: {request.program_id}")
    
    # Verify program exists
    program_config = config_service.get_program_by_id(request.program_id)
    if not program_config:
        raise HTTPException(status_code=404, detail=f"Program with ID '{request.program_id}' not found")
    
    if not program_config.get("enabled", True):
        raise HTTPException(status_code=400, detail=f"Program '{request.program_id}' is disabled")
    
    print(f"✅ Program config found: {program_config['name']}")
    
    # Generate execution ID
    import uuid
    execution_id = str(uuid.uuid4())
    print(f"🆔 Generated execution ID: {execution_id}")
    
    # Create execution record
    storage = ExecutionStorage()
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
        execution_service.execute_program,
        execution_id,
        request.program_id,
        request.parameters
    )
    
    print(f"🔄 Added background task")
    
    # Add execution to storage
    storage.add_execution(execution)
    print(f"💾 Added execution to storage")
    
    print(f"🎯 Returning response")
    
    return ExecutionResponse(
        execution_id=execution_id,
        program_id=request.program_id,
        status="queued",
        message=f"Program '{request.program_id}' queued for execution",
        timestamp=datetime.now()
    )


@router.get("", response_model=List[ExecutionStatus])
async def list_executions(
    current_user: str = Depends(get_current_user),
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """List all executions"""
    print("🔍 /executions endpoint called")
    return list(storage.get_executions().values())


@router.get("/info", response_model=Dict[str, Any])
async def get_executions_info(
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """Get information about execution storage"""
    return storage.get_stats()


@router.get("/stats", response_model=Dict[str, Any])
async def get_executions_stats(
    current_user: str = Depends(get_current_user),
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """Get execution statistics with detailed program breakdown"""
    executions = storage.get_executions()
    
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
            "max_executions": ExecutionStorage.MAX_EXECUTIONS,
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
        "max_executions": ExecutionStorage.MAX_EXECUTIONS,
        "concurrent_executions": concurrent_count
    }


@router.get("/concurrent", response_model=Dict[str, Any])
async def get_concurrent_executions(
    config_service: ConfigService = Depends(get_config_service),
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """Get information about currently running executions"""
    config = config_service.load_config()
    executions = storage.get_executions()
    
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


@router.delete("/cleanup")
async def cleanup_executions(
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """Manually clean all finished executions"""
    return storage.manual_cleanup_executions()


@router.get("/{execution_id}", response_model=ExecutionStatus)
async def get_execution_status(
    execution_id: str,
    current_user: str = Depends(get_current_user),
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """Get execution status"""
    executions = storage.get_executions()
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return executions[execution_id]


@router.get("/{execution_id}/logs", response_model=Dict[str, Any])
async def get_execution_logs(
    execution_id: str,
    current_user: str = Depends(get_current_user),
    storage: ExecutionStorage = Depends(get_execution_storage)
):
    """Get execution logs with additional details"""
    executions = storage.get_executions()
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

