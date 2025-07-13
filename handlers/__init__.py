"""
Handlers module for Gmail MCP Server

This module provides MCP handlers for resources, tools, and message operations.
"""

from .resource_handlers import ResourceHandlers
from .tool_handlers import ToolHandlers
from .message_handlers import MessageHandlers

__all__ = [
    'ResourceHandlers',
    'ToolHandlers', 
    'MessageHandlers'
]