"""
MCP Tool Handlers
=================

This module defines MCP tools and their handlers.
Tools in MCP are actions that can be performed by AI models.

MCP Tools vs Resources:
- Tools: Actions you can PERFORM (like send email, search)
- Resources: Data you can READ (like inbox, sent items)

Each tool has:
- Name: Unique identifier
- Description: What the tool does
- Input Schema: JSON schema defining required parameters
- Handler: Function that executes the tool action
"""

import logging
from typing import List, Dict, Any

from mcp.types import Tool
import mcp.types as types

from handlers.message_handlers import MessageHandlers

logger = logging.getLogger(__name__)

class ToolHandlers:
    """
    Handles MCP tool operations.
    
    This class provides methods to:
    1. List available tools
    2. Execute tool actions
    3. Format tool responses for MCP
    """
    
    def __init__(self, message_handlers: MessageHandlers):
        """
        Initialize with MessageHandlers instance.
        
        Args:
            message_handlers: Instance of MessageHandlers class
        """
        self.message_handlers = message_handlers
    
    async def list_tools(self) -> List[Tool]:
        """
        List all available Gmail tools.
        
        Returns:
            List[Tool]: Available MCP tools
            
        Notes:
            - Input schemas define what parameters each tool expects
            - Required fields must be provided by the caller
            - Optional fields have default values or can be omitted
        """
        return [
            Tool(
                name="send_email",
                description="Send an email via Gmail",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address"
                        },
                        "subject": {
                            "type": "string", 
                            "description": "Email subject"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content"
                        },
                        "cc": {
                            "type": "string",
                            "description": "CC recipients (optional)"
                        },
                        "bcc": {
                            "type": "string", 
                            "description": "BCC recipients (optional)"
                        }
                    },
                    "required": ["to", "subject", "body"]  # These must be provided
                }
            ),
            Tool(
                name="search_emails",
                description="Search Gmail messages using Gmail query syntax",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_message",
                description="Get a specific Gmail message by ID with full content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Gmail message ID"
                        }
                    },
                    "required": ["message_id"]
                }
            ),
            Tool(
                name="mark_as_read",
                description="Mark a message as read (remove UNREAD label)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Gmail message ID"
                        }
                    },
                    "required": ["message_id"]
                }
            ),
            Tool(
                name="add_label",
                description="Add a label to a message",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Gmail message ID"
                        },
                        "label": {
                            "type": "string",
                            "description": "Label name to add"
                        }
                    },
                    "required": ["message_id", "label"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """
        Execute a tool with given arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments dictionary
            
        Returns:
            List[types.TextContent]: Tool execution results
            
        Notes:
            - Each tool returns a TextContent object
            - Error handling ensures graceful failures
            - Results are formatted as strings for MCP protocol
        """
        try:
            if name == "send_email":
                result = await self.message_handlers.send_email(**arguments)
            elif name == "search_emails":
                result = await self.message_handlers.search_emails(**arguments)
            elif name == "get_message":
                result = await self.message_handlers.get_message(**arguments)
            elif name == "mark_as_read":
                result = await self.message_handlers.mark_as_read(**arguments)
            elif name == "add_label":
                result = await self.message_handlers.add_label(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return [types.TextContent(type="text", text=str(result))]
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    def get_tool_help(self, tool_name: str) -> str:
        """
        Get help text for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            str: Help text explaining tool usage
        """
        help_text = {
            "send_email": """
            Send Email Tool Usage:
            - to: Recipient email address (required)
            - subject: Email subject line (required)
            - body: Email content (required)
            - cc: Carbon copy recipients (optional)
            - bcc: Blind carbon copy recipients (optional)
            
            Example: send_email(to="user@example.com", subject="Hello", body="How are you?")
            """,
            
            "search_emails": """
            Search Emails Tool Usage:
            - query: Gmail search query (required)
            - max_results: Maximum number of results (optional, default: 10)
            
            Query Examples:
            - "from:sender@example.com" (emails from specific sender)
            - "subject:meeting" (emails with meeting in subject)
            - "is:unread" (unread emails)
            - "has:attachment" (emails with attachments)
            """,
            
            "get_message": """
            Get Message Tool Usage:
            - message_id: Gmail message ID (required)
            
            Returns full message content including headers and body.
            Message ID can be obtained from search results or resource listings.
            """,
            
            "mark_as_read": """
            Mark as Read Tool Usage:
            - message_id: Gmail message ID (required)
            
            Removes the UNREAD label from the message.
            """,
            
            "add_label": """
            Add Label Tool Usage:
            - message_id: Gmail message ID (required)
            - label: Label name to add (required)
            
            Label must already exist in Gmail.
            Use get_labels resource to see available labels.
            """
        }
        
        return help_text.get(tool_name, "Tool not found")