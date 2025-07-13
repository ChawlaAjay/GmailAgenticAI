"""
Gmail MCP Server - Main MCP Server Class
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional, Sequence

# MCP imports
try:
    from mcp.server import Server
    from mcp.types import Resource, Tool, TextContent, LoggingLevel
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("Error: MCP library not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Local imports
from auth.gmail_auth import GmailAuthenticator
from handlers.resource_handlers import ResourceHandlers
from handlers.tool_handlers import ToolHandlers
from handlers.message_handlers import MessageHandlers
from utils.logging_config import get_logger, log_mcp_event, LogFunctionExecution
from models.gmail_models import ToolResponse


class GmailMCPServer:
    """Main Gmail MCP Server class that orchestrates all components"""
    
    def __init__(self, server_name: str = "gmail-mcp-server"):
        self.server_name = server_name
        self.app = Server(server_name)
        self.logger = get_logger("gmail-mcp-server.server")
        
        # Initialize components
        self.authenticator = GmailAuthenticator()
        self.resource_handlers = None
        self.tool_handlers = None
        self.message_handlers = None
        
        # Gmail service will be set after authentication
        self.gmail_service = None
        
        # Setup MCP handlers
        self.setup_handlers()
        
        self.logger.info(f"Gmail MCP Server '{server_name}' initialized")
    
    def setup_handlers(self):
        """Setup all MCP handlers"""
        self.logger.debug("Setting up MCP handlers")
        
        # Resource handlers
        @self.app.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available Gmail resources"""
            with LogFunctionExecution("handle_list_resources"):
                log_mcp_event("list_resources", "Listing available resources")
                
                if not self.resource_handlers:
                    await self._ensure_authenticated()
                
                return await self.resource_handlers.list_resources()
        
        @self.app.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read Gmail resource content"""
            with LogFunctionExecution("handle_read_resource"):
                log_mcp_event("read_resource", f"Reading resource: {uri}")
                
                if not self.resource_handlers:
                    await self._ensure_authenticated()
                
                return await self.resource_handlers.read_resource(uri)
        
        # Tool handlers
        @self.app.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available Gmail tools"""
            with LogFunctionExecution("handle_list_tools"):
                log_mcp_event("list_tools", "Listing available tools")
                
                if not self.tool_handlers:
                    await self._ensure_authenticated()
                
                return await self.tool_handlers.list_tools()
        
        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            with LogFunctionExecution("handle_call_tool"):
                log_mcp_event("call_tool", f"Calling tool: {name}")
                
                if not self.tool_handlers:
                    await self._ensure_authenticated()
                
                try:
                    result = await self.tool_handlers.call_tool(name, arguments)
                    
                    # Convert result to TextContent
                    if isinstance(result, ToolResponse):
                        return [types.TextContent(type="text", text=result.to_json())]
                    else:
                        return [types.TextContent(type="text", text=str(result))]
                    
                except Exception as e:
                    self.logger.error(f"Error executing tool {name}: {e}")
                    error_response = ToolResponse(
                        success=False,
                        message=f"Tool execution failed: {str(e)}"
                    )
                    return [types.TextContent(type="text", text=error_response.to_json())]
        
        self.logger.debug("MCP handlers setup completed")
    
    async def _ensure_authenticated(self):
        """Ensure Gmail authentication is complete and initialize handlers"""
        if not self.gmail_service:
            self.logger.info("Authenticating with Gmail API")
            # Fixed: Remove await since authenticate() is synchronous
            success = self.authenticator.authenticate()
            
            if not success:
                raise Exception("Gmail authentication failed")
            
            self.gmail_service = self.authenticator.get_service()
            self.logger.info("Gmail authentication successful")
            
            # Initialize handlers with Gmail service
            self.message_handlers = MessageHandlers(self.gmail_service)
            self.resource_handlers = ResourceHandlers(self.message_handlers)
            self.tool_handlers = ToolHandlers(self.message_handlers)
            
            self.logger.info("Gmail MCP Server components initialized")
    
    async def initialize(self):
        """Initialize the server and authenticate with Gmail"""
        self.logger.info("Initializing Gmail MCP Server")
        
        try:
            await self._ensure_authenticated()
            self.logger.info("Gmail MCP Server initialization completed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail MCP Server: {e}")
            return False
    
    async def run(self):
        """Run the MCP server"""
        self.logger.info("Starting Gmail MCP Server")
        
        # Initialize server
        if not await self.initialize():
            self.logger.error("Server initialization failed. Exiting.")
            return
        
        log_mcp_event("server_start", "Gmail MCP Server started successfully")
        
        try:
            # Run the MCP server with stdio transport
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options()
                )
        except Exception as e:
            self.logger.error(f"Server runtime error: {e}")
            raise
        finally:
            self.logger.info("Gmail MCP Server stopped")
    
    async def shutdown(self):
        """Gracefully shutdown the server"""
        self.logger.info("Shutting down Gmail MCP Server")
        
        # Cleanup resources
        if self.authenticator:
            # Note: authenticator cleanup would also need to be synchronous
            # await self.authenticator.cleanup()
            pass
        
        if self.message_handlers:
            await self.message_handlers.cleanup()
        
        log_mcp_event("server_stop", "Gmail MCP Server shutdown completed")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": self.server_name,
            "version": "1.0.0",
            "description": "Gmail MCP Server for AI integration",
            "authenticated": bool(self.gmail_service),
            "components": {
                "authenticator": bool(self.authenticator),
                "resource_handlers": bool(self.resource_handlers),
                "tool_handlers": bool(self.tool_handlers),
                "message_handlers": bool(self.message_handlers)
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get server health status"""
        try:
            status = {
                "status": "healthy",
                "timestamp": str(asyncio.get_event_loop().time()),
                "authenticated": bool(self.gmail_service),
                "components": {}
            }
            
            # Check authenticator
            if self.authenticator:
                status["components"]["authenticator"] = "active"
            else:
                status["components"]["authenticator"] = "inactive"
                status["status"] = "degraded"
            
            # Check Gmail service
            if self.gmail_service:
                status["components"]["gmail_service"] = "active"
            else:
                status["components"]["gmail_service"] = "inactive"
                status["status"] = "degraded"
            
            # Check handlers
            handler_status = {
                "resource_handlers": "active" if self.resource_handlers else "inactive",
                "tool_handlers": "active" if self.tool_handlers else "inactive",
                "message_handlers": "active" if self.message_handlers else "inactive"
            }
            
            status["components"].update(handler_status)
            
            # If any handler is inactive, mark as degraded
            if "inactive" in handler_status.values():
                status["status"] = "degraded"
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": str(asyncio.get_event_loop().time())
            }


class GmailMCPServerManager:
    """Manager class for Gmail MCP Server lifecycle"""
    
    def __init__(self, server_name: str = "gmail-mcp-server"):
        self.server_name = server_name
        self.server = None
        self.logger = get_logger("gmail-mcp-server.manager")
    
    async def start_server(self) -> bool:
        """Start the Gmail MCP Server"""
        try:
            self.logger.info(f"Starting Gmail MCP Server: {self.server_name}")
            
            self.server = GmailMCPServer(self.server_name)
            await self.server.run()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
        finally:
            if self.server:
                await self.server.shutdown()
    
    async def stop_server(self):
        """Stop the Gmail MCP Server"""
        if self.server:
            await self.server.shutdown()
            self.server = None
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status"""
        if not self.server:
            return {
                "status": "stopped",
                "server": None
            }
        
        return {
            "status": "running",
            "server": self.server.get_server_info(),
            "health": self.server.get_health_status()
        }


# Factory function for creating server instances
def create_gmail_mcp_server(server_name: str = "gmail-mcp-server") -> GmailMCPServer:
    """Factory function to create Gmail MCP Server instance"""
    return GmailMCPServer(server_name)


# Utility function for running server
async def run_gmail_mcp_server(server_name: str = "gmail-mcp-server"):
    """Utility function to run Gmail MCP Server"""
    manager = GmailMCPServerManager(server_name)
    return await manager.start_server()