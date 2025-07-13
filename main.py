#!/usr/bin/env python3
"""
Gmail MCP Server - Entry Point
==============================

This is the main entry point for the Gmail MCP server.
It handles initial setup, validation, and starts the server.

Key responsibilities:
- Validate required files exist
- Initialize the MCP server
- Handle startup errors gracefully
- Provide helpful error messages to users
"""

import asyncio
import os
import sys
from pathlib import Path

# Import our custom modules
from server.mcp_server import GmailMCPServer
from utils.logging_config import setup_logging
from config.settings import CREDENTIALS_FILE, SETUP_INSTRUCTIONS

def validate_setup():
    """
    Validate that required files exist for Gmail API access.
    
    Returns:
        bool: True if setup is valid, False otherwise
        
    Notes:
        - Checks for credentials.json from Google Cloud Console
        - Provides helpful setup instructions if missing
        - Uses stderr for error messages (MCP protocol requirement)
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print("Error: credentials.json not found!", file=sys.stderr)
        print(f"Looking for credentials at: {CREDENTIALS_FILE}", file=sys.stderr)
        print("\nTo set up Gmail API access:", file=sys.stderr)
        for instruction in SETUP_INSTRUCTIONS:
            print(f"  {instruction}", file=sys.stderr)
        return False
    return True

async def main():
    """
    Main async function that runs the Gmail MCP server.
    
    Flow:
    1. Setup logging
    2. Validate configuration
    3. Initialize server
    4. Run server with MCP stdio communication
    """
    # Setup logging (configured to use stderr, not stdout)
    logger = setup_logging()
    
    # Validate that we have the required credentials
    if not validate_setup():
        sys.exit(1)
    
    # Initialize the Gmail MCP server
    server = GmailMCPServer()
    
    try:
        logger.info("Starting Gmail MCP Server...")
        
        # The server handles stdio communication internally
        await server.run()
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    """
    Entry point when script is run directly.
    
    Uses asyncio.run() to handle the async main function.
    This is the modern way to run async code in Python.
    """
    asyncio.run(main())