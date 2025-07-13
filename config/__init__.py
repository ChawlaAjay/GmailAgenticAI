"""
Gmail MCP Server - Configuration Package
========================================

This package provides configuration and settings for the Gmail MCP Server.
All configuration constants, file paths, and settings are centralized here.
"""

from .settings import (
    # Paths
    PROJECT_ROOT,
    CREDENTIALS_FILE,
    TOKEN_FILE,
    
    # Gmail API Configuration
    SCOPES,
    
    # Default Values
    DEFAULT_MAX_RESULTS,
    DEFAULT_PORT,
    
    # MCP Server Configuration
    SERVER_NAME,
    SERVER_VERSION,
    
    # Setup Instructions
    SETUP_INSTRUCTIONS,
    
    # Error Messages
    ERROR_MESSAGES,
    
    # Logging Configuration
    LOG_LEVEL,
    LOG_FORMAT
)

__all__ = [
    # Paths
    'PROJECT_ROOT',
    'CREDENTIALS_FILE',
    'TOKEN_FILE',
    
    # Gmail API Configuration
    'SCOPES',
    
    # Default Values
    'DEFAULT_MAX_RESULTS',
    'DEFAULT_PORT',
    
    # MCP Server Configuration
    'SERVER_NAME',
    'SERVER_VERSION',
    
    # Setup Instructions
    'SETUP_INSTRUCTIONS',
    
    # Error Messages
    'ERROR_MESSAGES',
    
    # Logging Configuration
    'LOG_LEVEL',
    'LOG_FORMAT'
]