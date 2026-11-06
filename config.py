"""
 Re-exporta as configurações centralizadas de src.config
"""
from src.config import Settings, settings
from src.version import VERSION, APP_NAME

__all__ = ["Settings", "settings", "VERSION", "APP_NAME"]
