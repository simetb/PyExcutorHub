"""Configuration service"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional


class ConfigService:
    """Service for managing configuration"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(os.getenv("PROJECT_DIR", "/app"))
        self.docker_image = "pyexecutorhub-base"  # Default, will be overridden by config
    
    def load_config(self) -> Dict:
        """Load configuration from config.yaml"""
        config_path = self.base_dir / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError("config.yaml not found")
        
        print(f"📄 Loading config from: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # Update default docker image from config
            self.docker_image = config.get("settings", {}).get("docker_image", "pyexecutorhub-base")
            print(f"✅ Config loaded successfully, found {len(config.get('scripts', {}))} scripts and {len(config.get('bots', {}))} bots")
            return config
    
    def get_program_by_id(self, program_id: str) -> Optional[Dict]:
        """Find a program by ID in the configuration"""
        config = self.load_config()
        
        # Search in scripts by key or internal id
        for script_id, script_config in config.get("scripts", {}).items():
            if script_id == program_id or script_config.get("id") == program_id:
                script_config["type"] = "script"
                return script_config
        
        # Search in bots by key or internal id
        for bot_id, bot_config in config.get("bots", {}).items():
            if bot_id == program_id or bot_config.get("id") == program_id:
                bot_config["type"] = "bot"
                return bot_config
        
        return None

