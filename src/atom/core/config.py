"""
Configuration management for Atom.
Loads settings from config.yaml file.
"""

import yaml
from pathlib import Path
from atom.utils.logger import setup_logger

logger = setup_logger(__name__, 'atom.log')

class Config:
    """Configuration manager for Atom settings."""
    
    def __init__(self, config_file='config/config.yaml'):
        """
        Load configuration from YAML file.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                logger.warning(f"Config file {self.config_file} not found. Using defaults.")
                return self._get_default_config()
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
                
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Return default configuration."""
        return {
            'bot': {
                'name': 'Nirav',
                'username': 'Meet',
                'voice_rate': 170,
                'voice_index': 0
            },
            'model': {
                'confidence_threshold': 0.75,
                'hidden_size': 8,
                'num_epochs': 1000,
                'batch_size': 8,
                'learning_rate': 0.001,
                'model_file': 'TrainData.pth',
                'intents_file': 'intents.json'
            },
            'audio': {
                'language': 'en-in',
                'pause_threshold': 1,
                'listen_timeout': 0,
                'phrase_time_limit': 4
            },
            'validation': {
                'max_input_length': 500,
                'enable_sanitization': True
            },
            'logging': {
                'level': 'INFO',
                'log_file': 'atom.log',
                'log_to_console': True,
                'log_to_file': True
            },
            'features': {
                'enable_wikipedia': True,
                'enable_google_search': True,
                'enable_youtube': True,
                'enable_time_commands': True
            }
        }
    
    def get(self, key_path, default=None):
        """
        Get configuration value by key path.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'bot.name')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Config key '{key_path}' not found, using default: {default}")
            return default
    
    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        logger.info("Configuration reloaded")


# Global configuration instance
_config = None

def get_config():
    """
    Get global configuration instance.
    
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
