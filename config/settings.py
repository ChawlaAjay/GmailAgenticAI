"""
Configuration and Settings for Gmail MCP Server
===============================================

This file contains all configuration constants and settings.
Centralizing config makes it easier to manage and modify.

Key concepts:
- SCOPES: Define what Gmail permissions we need
- File paths: Where to store credentials and tokens
- Default values: Fallback values for optional parameters
"""

import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Gmail API Configuration
# =======================
# Scopes define what permissions your app needs from Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.send',      # Send emails  
    'https://www.googleapis.com/auth/gmail.modify'     # Modify emails (mark read, add labels)
]

# File Paths
# ==========
# These paths are relative to the project root
CREDENTIALS_FILE = PROJECT_ROOT / 'config' / 'credentials.json'
TOKEN_FILE = PROJECT_ROOT / 'auth' / 'token.json'

# Default Values
# ==============
DEFAULT_MAX_RESULTS = 10  # Default number of emails to fetch
DEFAULT_PORT = 0         # Let OAuth choose available port

# MCP Server Configuration
# =======================
SERVER_NAME = "gmail-mcp-server"
SERVER_VERSION = "1.0.0"

# Setup Instructions
# ==================
# Helpful instructions for users who haven't set up Gmail API
SETUP_INSTRUCTIONS = [
    "1. Go to Google Cloud Console (https://console.cloud.google.com/)",
    "2. Create a new project or select existing one",
    "3. Enable Gmail API",
    "4. Create OAuth 2.0 credentials (Desktop application)",
    "5. Download as 'credentials.json' and place in config/ directory"
]

# Error Messages
# ==============
ERROR_MESSAGES = {
    'auth_failed': "Gmail authentication failed. Please check your credentials.",
    'api_error': "Gmail API error occurred. Please try again.",
    'invalid_message_id': "Invalid message ID provided.",
    'label_not_found': "Specified label not found.",
    'permission_denied': "Permission denied. Check your Gmail API scopes."
}

# Logging Configuration
# ====================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"