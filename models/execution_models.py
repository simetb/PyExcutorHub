"""Execution models"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    program_id: str = Field(..., description="ID of the program to execute")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Additional parameters")


class ExecutionResponse(BaseModel):
    execution_id: str
    program_id: str
    status: str
    message: str
    timestamp: datetime


class ExecutionStatus(BaseModel):
    execution_id: str
    program_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None

