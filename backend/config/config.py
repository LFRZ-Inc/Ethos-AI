"""
Configuration management for Ethos AI
Handles settings, API keys, and model configurations
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a single model"""
    id: str
    name: str
    type: str  # local, cloud
    provider: str  # ollama, anthropic, openai, etc.
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    capabilities: list = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class ToolConfig:
    """Configuration for tools"""
    python_execution: bool = True
    web_search: bool = True
    file_search: bool = True
    code_execution: bool = True
    sandbox_mode: bool = True

@dataclass
class MemoryConfig:
    """Configuration for memory system"""
    vector_store: str = "chromadb"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_memory_size: int = 10000
    similarity_threshold: float = 0.7

@dataclass
class UIConfig:
    """Configuration for UI settings"""
    theme: str = "dark"
    language: str = "en"
    auto_save: bool = True
    max_conversations: int = 100

class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.data_dir = self._get_data_dir()
        
        # Load configuration
        self._load_config()
        
        # Initialize sub-configs
        self.models = self._load_models()
        self.tools = ToolConfig(**self.config.get("tools", {}))
        self.memory = MemoryConfig(**self.config.get("memory", {}))
        self.ui = UIConfig(**self.config.get("ui", {}))
        
        # Create data directories
        self._create_directories()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        config_dir = Path.home() / ".ethos_ai" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.yaml")
    
    def _get_data_dir(self) -> str:
        """Get data directory path"""
        data_dir = Path.home() / "EthosAIData"
        return str(data_dir)
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                self.config = self._get_default_config()
                self._save_config()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "models": {
                "llama3-70b": {
                    "name": "LLaMA 3 70B",
                    "type": "local",
                    "provider": "ollama",
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["general_chat", "reasoning"],
                    "parameters": {
                        "model": "llama3.2:70b",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "enabled": True
                },
                "deepseek-r1": {
                    "name": "DeepSeek R1",
                    "type": "local",
                    "provider": "ollama",
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["math", "logic", "reasoning"],
                    "parameters": {
                        "model": "deepseek-coder:33b",
                        "temperature": 0.3,
                        "max_tokens": 4096
                    },
                    "enabled": True
                },
                "codellama": {
                    "name": "CodeLLaMA",
                    "type": "local",
                    "provider": "ollama",
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["coding", "programming"],
                    "parameters": {
                        "model": "codellama:34b",
                        "temperature": 0.2,
                        "max_tokens": 4096
                    },
                    "enabled": True
                },
                "llava-next": {
                    "name": "LLaVA Next",
                    "type": "local",
                    "provider": "ollama",
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["image_analysis", "vision"],
                    "parameters": {
                        "model": "llava:latest",
                        "temperature": 0.7,
                        "max_tokens": 2048
                    },
                    "enabled": True
                },
                "claude-3.5": {
                    "name": "Claude 3.5 Sonnet",
                    "type": "cloud",
                    "provider": "anthropic",
                    "capabilities": ["general_chat", "reasoning", "writing"],
                    "parameters": {
                        "model": "claude-3-5-sonnet-20241022",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "enabled": False  # Disabled to avoid charges
                },
                "gpt-4": {
                    "name": "GPT-4",
                    "type": "cloud",
                    "provider": "openai",
                    "capabilities": ["general_chat", "reasoning"],
                    "parameters": {
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    },
                    "enabled": False  # Disabled to avoid charges
                }
            },
            "orchestration": {
                "routing": {
                    "math_logic": ["deepseek-r1", "llama3-70b"],
                    "coding": ["codellama", "deepseek-r1"],
                    "general_chat": ["llama3-70b", "deepseek-r1"],
                    "image_analysis": ["llava-next"],
                    "image_generation": ["flux-1"]
                },
                "fallback_order": ["llama3-70b", "deepseek-r1", "codellama"],
                "prefer_local": True,
                "max_retries": 3
            },
            "tools": {
                "python_execution": True,
                "web_search": True,
                "file_search": True,
                "code_execution": True,
                "sandbox_mode": True
            },
            "memory": {
                "vector_store": "chromadb",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "max_memory_size": 10000,
                "similarity_threshold": 0.7
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "auto_save": True,
                "max_conversations": 100
            },
            "api_keys": {
                "anthropic": "",
                "openai": "",
                "huggingface": ""
            }
        }
    
    def _load_models(self) -> Dict[str, ModelConfig]:
        """Load model configurations"""
        models = {}
        for model_id, model_data in self.config.get("models", {}).items():
            models[model_id] = ModelConfig(
                id=model_id,
                **model_data
            )
        return models
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _create_directories(self):
        """Create necessary data directories"""
        directories = [
            self.data_dir,
            f"{self.data_dir}/conversations",
            f"{self.data_dir}/embeddings",
            f"{self.data_dir}/models",
            f"{self.data_dir}/uploads",
            f"{self.data_dir}/exports",
            f"{self.data_dir}/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.models.get(model_id)
    
    def get_enabled_models(self) -> Dict[str, ModelConfig]:
        """Get all enabled models"""
        return {k: v for k, v in self.models.items() if v.enabled}
    
    def get_models_by_capability(self, capability: str) -> Dict[str, ModelConfig]:
        """Get models that support a specific capability"""
        return {
            k: v for k, v in self.models.items() 
            if v.enabled and capability in v.capabilities
        }
    
    def get_orchestration_rules(self) -> Dict[str, Any]:
        """Get orchestration rules"""
        return self.config.get("orchestration", {})
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider - check environment variables first"""
        # Check environment variables first
        env_key = f"ETHOS_AI_{provider.upper()}_API_KEY"
        env_value = os.getenv(env_key)
        if env_value:
            return env_value
        
        # Fall back to config file
        return self.config.get("api_keys", {}).get(provider)
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider"""
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][provider] = api_key
        self._save_config()
    
    def update_config(self, config_data: Dict[str, Any]):
        """Update configuration"""
        # Update models
        if "models" in config_data:
            for model_id, model_data in config_data["models"].items():
                if model_id in self.models:
                    for key, value in model_data.items():
                        setattr(self.models[model_id], key, value)
        
        # Update other configs
        if "tools" in config_data:
            for key, value in config_data["tools"].items():
                setattr(self.tools, key, value)
        
        if "memory" in config_data:
            for key, value in config_data["memory"].items():
                setattr(self.memory, key, value)
        
        if "ui" in config_data:
            for key, value in config_data["ui"].items():
                setattr(self.ui, key, value)
        
        # Update main config
        self.config.update(config_data)
        self._save_config()
    
    def get_public_config(self) -> Dict[str, Any]:
        """Get public configuration (without sensitive data)"""
        public_config = {
            "models": {},
            "orchestration": self.config.get("orchestration", {}),
            "tools": self.config.get("tools", {}),
            "memory": self.config.get("memory", {}),
            "ui": self.config.get("ui", {})
        }
        
        # Add model configs without API keys
        for model_id, model_config in self.models.items():
            public_config["models"][model_id] = {
                "name": model_config.name,
                "type": model_config.type,
                "provider": model_config.provider,
                "capabilities": model_config.capabilities,
                "parameters": model_config.parameters,
                "enabled": model_config.enabled
            }
        
        return public_config
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            # Check if at least one model is enabled
            enabled_models = self.get_enabled_models()
            if not enabled_models:
                logger.error("No models are enabled")
                return False
            
            # Check if data directory is accessible
            if not os.access(self.data_dir, os.W_OK):
                logger.error(f"Data directory {self.data_dir} is not writable")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False 