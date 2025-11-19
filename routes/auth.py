"""Authentication routes"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.auth_models import LoginRequest, LoginResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Global auth service instance (will be set by main app)
_auth_service: Optional[AuthService] = None


def set_auth_service(auth_service: AuthService):
    """Set the auth service instance"""
    global _auth_service
    _auth_service = auth_service


def get_auth_service() -> AuthService:
    """Dependency to get auth service"""
    if _auth_service is None:
        raise HTTPException(status_code=500, detail="Auth service not initialized")
    return _auth_service


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    username = auth_service.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with username and password to get access token"""
    # Check if credentials match
    if (request.username != auth_service.auth_credentials.username or 
        not auth_service.verify_password(request.password, auth_service.get_password_hash(auth_service.auth_credentials.password))):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": request.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=auth_service.access_token_expire_minutes * 60,  # Convert to seconds
        username=request.username
    )

