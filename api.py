#!/usr/bin/env python3
"""
Serverless Docker API
FastAPI for executing scripts and bots in Docker containers
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI

from models.execution_models import ExecutionRequest, ExecutionResponse
from routes import auth, programs, executions, containers, images
from services.auth_service import AuthService
from services.config_service import ConfigService
from services.execution_service import ExecutionService


class ServerlessAPI:
    def __init__(self):
        print("🚀 Initializing ServerlessAPI...")
        self.app = FastAPI(
            title="Serverless Docker API",
            description="API for executing scripts and bots in isolated Docker containers",
            version="1.0.0"
        )
        print("📋 FastAPI app created")
        
        # Initialize services
        self.base_dir = Path(os.getenv("PROJECT_DIR", "/app"))
        self.config_service = ConfigService(self.base_dir)
        self.auth_service = AuthService()
        self.execution_service = ExecutionService(self.config_service)
        
        print("⚙️ Services initialized")
        print("🔧 Setting up routes...")
        self.setup_routes()
        print("✅ ServerlessAPI initialization complete")
    
    def setup_routes(self):
        """Setup API routes"""
        
        # Initialize auth credentials
        self.auth_service.initialize_credentials()
        
        # Inject services into routers
        auth.set_auth_service(self.auth_service)
        programs.set_config_service(self.config_service)
        executions.set_config_service(self.config_service)
        executions.set_execution_service(self.execution_service)
        images.set_config_service(self.config_service)
        
        # Root endpoint
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint"""
            return {
                "message": "Serverless Docker API",
                "version": "1.0.0",
                "status": "running",
                "container": "docker"
            }
        
        # Health check endpoint
        @self.app.get("/health", response_model=Dict[str, str])
        async def health_check():
            """API health check"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        # Test endpoint
        @self.app.get("/test", response_model=Dict[str, str])
        async def test_endpoint():
            """Test endpoint to verify basic functionality"""
            print("🧪 Test endpoint called")
            return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}
        
        # Include routers
        self.app.include_router(auth.router)
        self.app.include_router(programs.router)
        self.app.include_router(executions.router)
        self.app.include_router(containers.router)
        self.app.include_router(images.router)
        
        # Add /execute endpoint (legacy compatibility - redirects to /executions)
        @self.app.post("/execute", response_model=ExecutionResponse)
        async def execute_program_legacy(
            request: ExecutionRequest,
            background_tasks: BackgroundTasks,
            current_user: str = Depends(auth.get_current_user),
            config_service: ConfigService = Depends(programs.get_config_service),
            execution_service: ExecutionService = Depends(executions.get_execution_service)
        ):
            """Execute a program (legacy endpoint)"""
            from routes.executions import execute_program
            return await execute_program(request, background_tasks, current_user, config_service, execution_service)
        
        print("✅ All routes registered")


# Create API instance
api = ServerlessAPI()
app = api.app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
