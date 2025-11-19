"""Authentication service"""
import os
import re
import secrets
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from models.auth_models import AuthCredentials


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours
        self.pwd_context = CryptContext(schemes=["plaintext"], deprecated="auto")
        self.auth_credentials: Optional[AuthCredentials] = None
    
    def generate_random_credentials(self) -> AuthCredentials:
        """Generate random username and password at startup"""
        # Generate random username (8 characters)
        username = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        
        # Generate random password (10 characters with mixed case and digits only)
        # No special characters to avoid issues with shell scripts and curl
        password_chars = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(password_chars) for _ in range(10))
        
        return AuthCredentials(
            username=username,
            password=password,
            created_at=datetime.now()
        )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the username"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
    
    def update_cron_script(self, username: str, password: str) -> bool:
        """Update credentials in cron script files"""
        try:
            # Get project directory
            project_dir = Path(os.getenv("PROJECT_DIR", "/app"))
            
            # Possible cron script locations
            cron_scripts = [
                project_dir / "cron" / "execute_bot.sh",
                project_dir / "cron" / "execute_cron.sh",
                Path("/apps/PyExecutorHub/cron/execute_cron.sh"),  # Production path
            ]
            
            updated_files = []
            
            for script_path in cron_scripts:
                if script_path.exists() and script_path.is_file():
                    try:
                        # Read the file
                        with open(script_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check if file has USERNAME and PASSWORD variables
                        if 'USERNAME=' in content or 'PASSWORD=' in content:
                            # Update USERNAME (handle various formats including empty values)
                            content = re.sub(
                                r'USERNAME=["\']?[^"\'\n]*["\']?',
                                f'USERNAME="{username}"',
                                content
                            )
                            
                            # Update PASSWORD (handle various formats including empty values)
                            content = re.sub(
                                r'PASSWORD=["\']?[^"\'\n]*["\']?',
                                f'PASSWORD="{password}"',
                                content
                            )
                            
                            # Write back the file
                            with open(script_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            # Ensure executable permissions
                            os.chmod(script_path, 0o755)
                            
                            updated_files.append(str(script_path))
                            print(f"✅ Updated credentials in: {script_path}")
                    except Exception as e:
                        print(f"⚠️ Warning: Could not update {script_path}: {e}")
            
            if updated_files:
                print(f"📝 Updated {len(updated_files)} cron script(s) with new credentials")
                return True
            else:
                print("ℹ️ No cron scripts found to update (this is OK if not using cron)")
                return False
                
        except Exception as e:
            print(f"⚠️ Warning: Error updating cron scripts: {e}")
            return False
    
    def initialize_credentials(self) -> AuthCredentials:
        """Initialize and return credentials"""
        if self.auth_credentials is None:
            self.auth_credentials = self.generate_random_credentials()
            print("\n" + "=" * 60)
            print("🔐 AUTHENTICATION CREDENTIALS")
            print("=" * 60)
            print(f"👤 Username: {self.auth_credentials.username}")
            print(f"🔑 Password: {self.auth_credentials.password}")
            print("=" * 60)
            print("💡 Use these credentials to login at /auth/login")
            print("🔒 Credentials are shown only once for security")
            print("=" * 60 + "\n")
            
            # Update cron scripts automatically
            self.update_cron_script(
                self.auth_credentials.username,
                self.auth_credentials.password
            )
        return self.auth_credentials

