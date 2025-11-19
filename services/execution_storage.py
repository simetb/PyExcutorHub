"""Execution storage service"""
from datetime import datetime
from typing import Dict

from models.execution_models import ExecutionStatus

# Global state for execution tracking
executions: Dict[str, ExecutionStatus] = {}
MAX_EXECUTIONS = 100  # Memory execution limit


class ExecutionStorage:
    """Service for managing execution storage"""
    
    @staticmethod
    def get_executions() -> Dict[str, ExecutionStatus]:
        """Get all executions"""
        return executions
    
    @staticmethod
    def get_execution(execution_id: str) -> ExecutionStatus:
        """Get a specific execution"""
        return executions[execution_id]
    
    @staticmethod
    def add_execution(execution: ExecutionStatus):
        """Add an execution"""
        executions[execution.execution_id] = execution
    
    @staticmethod
    def update_execution(execution_id: str, **kwargs):
        """Update an execution"""
        if execution_id in executions:
            for key, value in kwargs.items():
                setattr(executions[execution_id], key, value)
    
    @staticmethod
    def delete_execution(execution_id: str):
        """Delete an execution"""
        if execution_id in executions:
            del executions[execution_id]
    
    @staticmethod
    def cleanup_old_executions():
        """Remove oldest executions when limit is reached"""
        if len(executions) >= MAX_EXECUTIONS:
            # Only consider executions that are finished (completed, failed, timeout)
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
    
    @staticmethod
    def manual_cleanup_executions():
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
    
    @staticmethod
    def get_stats():
        """Get execution statistics"""
        return {
            "total_executions": len(executions),
            "max_executions": MAX_EXECUTIONS,
            "available_slots": MAX_EXECUTIONS - len(executions),
            "storage_type": "memory",
            "cleanup_enabled": True
        }

