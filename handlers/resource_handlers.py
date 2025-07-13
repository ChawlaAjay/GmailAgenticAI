"""
MCP Resource Handlers
=====================

This module defines MCP resources and their handlers.
Resources in MCP are data sources that can be read by AI models.

MCP Resources vs Tools:
- Resources: Data you can READ (like inbox, sent items)
- Tools: Actions you can PERFORM (like send email, search)

Each resource has:
- URI: Unique identifier (like gmail://inbox)
- Name: Human-readable name
- Description: What the resource contains
- Handler: Function that returns the resource data
"""

import json
import logging
from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from mcp.types import Resource
from config.settings import DEFAULT_MAX_RESULTS

logger = logging.getLogger(__name__)

class ResourceHandlers:
    """
    Handles MCP resource operations.
    
    This class provides methods to:
    1. List available resources
    2. Read resource content
    3. Format resource data for MCP responses
    """
    
    def __init__(self, gmail_service):
        """
        Initialize with Gmail service.
        
        Args:
            gmail_service: Authenticated Gmail API service
        """
        self.service = gmail_service
    
    async def list_resources(self) -> List[Resource]:
        """
        List all available Gmail resources.
        
        Returns:
            List[Resource]: Available MCP resources
            
        Notes:
            - These are the data sources AI models can access
            - Each resource has a unique URI scheme
            - MimeType helps clients understand data format
        """
        return [
            Resource(
                uri="gmail://inbox",
                name="Gmail Inbox",
                description="Access Gmail inbox messages with sender, subject, date, and snippet",
                mimeType="application/json"
            ),
            Resource(
                uri="gmail://sent",
                name="Gmail Sent Items", 
                description="Access sent messages with recipient, subject, date, and snippet",
                mimeType="application/json"
            ),
            Resource(
                uri="gmail://labels",
                name="Gmail Labels",
                description="Access Gmail labels (folders) including system and custom labels",
                mimeType="application/json"
            )
        ]
    
    async def read_resource(self, uri: str) -> str:
        """
        Read content from a specific resource.
        
        Args:
            uri: Resource URI (e.g., "gmail://inbox")
            
        Returns:
            str: JSON-formatted resource content
            
        Raises:
            ValueError: If URI is not recognized
        """
        try:
            if uri == "gmail://inbox":
                return await self._get_inbox_messages()
            elif uri == "gmail://sent":
                return await self._get_sent_messages()
            elif uri == "gmail://labels":
                return await self._get_labels()
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            raise
    
    async def _get_inbox_messages(self, max_results: int = DEFAULT_MAX_RESULTS) -> str:
        """
        Get inbox messages with metadata.
        
        Args:
            max_results: Maximum number of messages to fetch
            
        Returns:
            str: JSON-formatted inbox messages
            
        Notes:
            - Uses 'INBOX' label to filter messages
            - Fetches only metadata (not full message body)
            - Includes sender, subject, date, and snippet
        """
        try:
            # Get list of message IDs in inbox
            results = self.service.users().messages().list(
                userId='me',           # 'me' refers to authenticated user
                labelIds=['INBOX'],    # Only inbox messages
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            inbox_data = []
            
            # Get metadata for each message
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',  # Only get headers, not body
                    metadataHeaders=['From', 'Subject', 'Date']  # Specific headers
                ).execute()
                
                # Extract headers into a dictionary
                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                
                inbox_data.append({
                    'id': message['id'],
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', 'Unknown'),
                    'snippet': message.get('snippet', '')  # Gmail's auto-generated preview
                })
            
            return json.dumps(inbox_data, indent=2)
            
        except HttpError as e:
            logger.error(f"HTTP error fetching inbox: {e}")
            return f"Error fetching inbox: {e}"
    
    async def _get_sent_messages(self, max_results: int = DEFAULT_MAX_RESULTS) -> str:
        """
        Get sent messages with metadata.
        
        Args:
            max_results: Maximum number of messages to fetch
            
        Returns:
            str: JSON-formatted sent messages
            
        Notes:
            - Uses 'SENT' label to filter messages
            - Similar to inbox but shows 'To' instead of 'From'
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['SENT'],     # Only sent messages
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            sent_data = []
            
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['To', 'Subject', 'Date']  # 'To' instead of 'From'
                ).execute()
                
                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                
                sent_data.append({
                    'id': message['id'],
                    'to': headers.get('To', 'Unknown'),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', 'Unknown'),
                    'snippet': message.get('snippet', '')
                })
            
            return json.dumps(sent_data, indent=2)
            
        except HttpError as e:
            logger.error(f"HTTP error fetching sent messages: {e}")
            return f"Error fetching sent messages: {e}"
    
    async def _get_labels(self) -> str:
        """
        Get all Gmail labels (folders).
        
        Returns:
            str: JSON-formatted labels list
            
        Notes:
            - Includes both system labels (INBOX, SENT, DRAFT)
            - Includes custom user-created labels
            - Labels are used for organizing emails
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            labels_data = [
                {
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type', 'user'),  # 'system' or 'user'
                    'messages_total': label.get('messagesTotal', 0),
                    'messages_unread': label.get('messagesUnread', 0)
                }
                for label in labels
            ]
            
            return json.dumps(labels_data, indent=2)
            
        except HttpError as e:
            logger.error(f"HTTP error fetching labels: {e}")
            return f"Error fetching labels: {e}"