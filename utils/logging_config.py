# """
# Logging Configuration
# =====================

# This module configures logging for the Gmail MCP Server.
# Important: MCP requires that log messages go to stderr, not stdout.
# stdout is reserved for MCP protocol communication.

# Logging Levels:
# - DEBUG: Detailed information for debugging
# - INFO: General information about program execution
# - WARNING: Something unexpected happened but program continues
# - ERROR: Serious problem that prevented a function from working
# - CRITICAL: Very serious error that may cause program to stop
# """

# import logging
# import sys
# from pathlib import Path
# from typing import Optional

# from config.settings import LOG_LEVEL, LOG_FORMAT, PROJECT_ROOT

# def setup_logging(log_level: str = LOG_LEVEL, log_file: Optional[str] = None) -> logging.Logger:
#     """
#     Setup logging configuration for the Gmail MCP Server.
    
#     Args:
#         log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#         log_file: Optional log file path
        
#     Returns:
#         logging.Logger: Configured logger instance
        
#     Notes:
#         - Uses stderr for console output (MCP requirement)
#         - Optionally writes to log file
#         - Formats messages with timestamp and level
#     """
    
#     # Convert string level to logging constant
#     numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
#     # Create logger
#     logger = logging.getLogger("gmail-mcp-server")
#     logger.setLevel(numeric_level)
    
#     # Clear any existing handlers
#     logger.handlers.clear()
    
#     # Create console handler (stderr only for MCP)
#     console_handler = logging.StreamHandler(sys.stderr)
#     console_handler.setLevel(numeric_level)
    
#     # Create formatter
#     formatter = logging.Formatter(LOG_FORMAT)
#     console_handler.setFormatter(formatter)
    
#     # Add console handler to logger
#     logger.addHandler(console_handler)
    
#     # Optional file handler
#     if log_file:
#         file_handler = create_file_handler(log_file, numeric_level, formatter)
#         logger.addHandler(file_handler)
    
#     # Prevent duplicate logs from parent loggers
#     logger.propagate = False
    
#     return logger

# def create_file_handler(log_file: str, level: int, formatter: logging.Formatter) -> logging.FileHandler:
#     """
#     Create a file handler for logging to file.
    
#     Args:
#         log_file: Path to log file
#         level: Logging level
#         formatter: Log formatter
        
#     Returns:
#         logging.FileHandler: Configured file handler
#     """
#     # Ensure log directory exists
#     log_path = Path(log_file)
#     log_path.parent.mkdir(parents=True, exist_ok=True)
    
#     file_handler = logging.FileHandler(log_file)
#     file_handler.setLevel(level)
#     file_handler.setFormatter(formatter)
    
#     return file_handler

# def get_logger(name: str) -> logging.Logger:
#     """
#     Get a logger instance with the specified name.
    
#     Args:
#         name: Logger name (usually __name__)
        
#     Returns:
#         logging.Logger: Logger instance
        
#     Notes:
#         - Creates child logger under main gmail-mcp-server logger
#         - Inherits configuration from parent logger
#     """
#     return logging.getLogger(f"gmail-mcp-server.{name}")

# class LoggingContextManager:
#     """
#     Context manager for temporary logging level changes.
    
#     Usage:
#         with LoggingContextManager('DEBUG'):
#             # Code that needs debug logging
#             pass
#     """
    
#     def __init__(self, temp_level: str):
#         self.temp_level = getattr(logging, temp_level.upper(), logging.INFO)
#         self.original_level = None
#         self.logger = logging.getLogger("gmail-mcp-server")
    
#     def __enter__(self):
#         self.original_level = self.logger.level
#         self.logger.setLevel(self.temp_level)
#         return self
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.logger.setLevel(self.original_level)

# def log_gmail_api_call(operation: str, details: str = ""):
#     """
#     Log Gmail API calls with consistent formatting.
    
#     Args:
#         operation: The API operation being performed
#         details: Additional details about the operation
#     """
#     logger = get_logger("gmail-api")
#     message = f"Gmail API: {operation}"
#     if details:
#         message += f" - {details}"
#     logger.info(message)

# def log_mcp_event(event_type: str, details: str = ""):
#     """
#     Log MCP protocol events with consistent formatting.
    
#     Args:
#         event_type: Type of MCP event
#         details: Additional details about the event
#     """
#     logger = get_logger("mcp-protocol")
#     message = f"MCP: {event_type}"
#     if details:
#         message += f" - {details}"
#     logger.info(message)

# def log_error_with_context(error: Exception, context: str = ""):
#     """
#     Log errors with additional context information.
    
#     Args:
#         error: The exception that occurred
#         context: Additional context about when/where error occurred
#     """
#     logger = get_logger("errors")
#     message = f"Error: {str(error)}"
#     if context:
#         message += f" (Context: {context})"
#     logger.error(message, exc_info=True)

# # Module-level logger for this file
# logger = get_logger(__name__)

"""
Logging Configuration
=====================

This module configures logging for the Gmail MCP Server.
Important: MCP requires that log messages go to stderr, not stdout.
stdout is reserved for MCP protocol communication.

Logging Levels:
- DEBUG: Detailed information for debugging
- INFO: General information about program execution
- WARNING: Something unexpected happened but program continues
- ERROR: Serious problem that prevented a function from working
- CRITICAL: Very serious error that may cause program to stop
"""

import logging
import sys
import time
import functools
from pathlib import Path
from typing import Optional, Callable, Any

from config.settings import LOG_LEVEL, LOG_FORMAT, PROJECT_ROOT

def setup_logging(log_level: str = LOG_LEVEL, log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration for the Gmail MCP Server.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        logging.Logger: Configured logger instance
        
    Notes:
        - Uses stderr for console output (MCP requirement)
        - Optionally writes to log file
        - Formats messages with timestamp and level
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("gmail-mcp-server")
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create console handler (stderr only for MCP)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Optional file handler
    if log_file:
        file_handler = create_file_handler(log_file, numeric_level, formatter)
        logger.addHandler(file_handler)
    
    # Prevent duplicate logs from parent loggers
    logger.propagate = False
    
    return logger

def create_file_handler(log_file: str, level: int, formatter: logging.Formatter) -> logging.FileHandler:
    """
    Create a file handler for logging to file.
    
    Args:
        log_file: Path to log file
        level: Logging level
        formatter: Log formatter
        
    Returns:
        logging.FileHandler: Configured file handler
    """
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    return file_handler

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
        
    Notes:
        - Creates child logger under main gmail-mcp-server logger
        - Inherits configuration from parent logger
    """
    return logging.getLogger(f"gmail-mcp-server.{name}")

class LoggingContextManager:
    """
    Context manager for temporary logging level changes.
    
    Usage:
        with LoggingContextManager('DEBUG'):
            # Code that needs debug logging
            pass
    """
    
    def __init__(self, temp_level: str):
        self.temp_level = getattr(logging, temp_level.upper(), logging.INFO)
        self.original_level = None
        self.logger = logging.getLogger("gmail-mcp-server")
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.temp_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)

class LogFunctionExecution:
    """
    Decorator/Context manager for logging function execution.
    
    Can be used as:
    1. Decorator: @LogFunctionExecution()
    2. Context manager: with LogFunctionExecution("operation_name"):
    """
    
    def __init__(self, operation_name: str = None, log_args: bool = False, log_result: bool = False):
        self.operation_name = operation_name
        self.log_args = log_args
        self.log_result = log_result
        self.logger = get_logger("function-execution")
        self.start_time = None
    
    def __call__(self, func: Callable) -> Callable:
        """Use as decorator"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            operation_name = self.operation_name or f"{func.__module__}.{func.__name__}"
            
            # Log function start
            start_time = time.time()
            log_message = f"Starting: {operation_name}"
            
            if self.log_args:
                log_message += f" with args={args}, kwargs={kwargs}"
            
            self.logger.info(log_message)
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                duration = time.time() - start_time
                log_message = f"Completed: {operation_name} in {duration:.3f}s"
                
                if self.log_result:
                    log_message += f" -> {result}"
                
                self.logger.info(log_message)
                return result
                
            except Exception as e:
                # Log error
                duration = time.time() - start_time
                self.logger.error(f"Failed: {operation_name} after {duration:.3f}s - {str(e)}")
                raise
        
        return wrapper
    
    def __enter__(self):
        """Use as context manager"""
        self.start_time = time.time()
        operation_name = self.operation_name or "operation"
        self.logger.info(f"Starting: {operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        duration = time.time() - self.start_time
        operation_name = self.operation_name or "operation"
        
        if exc_type is None:
            self.logger.info(f"Completed: {operation_name} in {duration:.3f}s")
        else:
            self.logger.error(f"Failed: {operation_name} after {duration:.3f}s - {str(exc_val)}")

def log_gmail_api_call(operation: str, details: str = ""):
    """
    Log Gmail API calls with consistent formatting.
    
    Args:
        operation: The API operation being performed
        details: Additional details about the operation
    """
    logger = get_logger("gmail-api")
    message = f"Gmail API: {operation}"
    if details:
        message += f" - {details}"
    logger.info(message)

def log_mcp_event(event_type: str, details: str = ""):
    """
    Log MCP protocol events with consistent formatting.
    
    Args:
        event_type: Type of MCP event
        details: Additional details about the event
    """
    logger = get_logger("mcp-protocol")
    message = f"MCP: {event_type}"
    if details:
        message += f" - {details}"
    logger.info(message)

def log_error_with_context(error: Exception, context: str = ""):
    """
    Log errors with additional context information.
    
    Args:
        error: The exception that occurred
        context: Additional context about when/where error occurred
    """
    logger = get_logger("errors")
    message = f"Error: {str(error)}"
    if context:
        message += f" (Context: {context})"
    logger.error(message, exc_info=True)

# Module-level logger for this file
logger = get_logger(__name__)