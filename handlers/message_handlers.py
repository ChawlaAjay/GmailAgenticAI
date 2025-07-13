"""
Gmail Message Operations
========================

This module handles specific Gmail API operations.
It provides methods for all Gmail actions like sending, searching, and managing messages.

Key Gmail API Concepts:
- Messages: Individual emails with unique IDs
- Threads: Conversations grouping related messages
- Labels: Gmail's version of folders (INBOX, SENT, custom labels)
- Formats: How much data to retrieve (metadata, full, minimal)
"""

import json
import logging
import base64
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.errors import HttpError
from config.settings import DEFAULT_MAX_RESULTS
from utils.email_utils import EmailParser

logger = logging.getLogger(__name__)

class MessageHandlers:
    """
    Handles Gmail message operations.
    
    This class provides methods for:
    - Sending emails
    - Searching messages
    - Getting message details
    - Managing message labels
    - Marking messages as read
    """
    
    def __init__(self, gmail_service):
        """
        Initialize with Gmail service.
        
        Args:
            gmail_service: Authenticated Gmail API service
        """
        self.service = gmail_service
        self.email_parser = EmailParser()
    
    async def send_email(self, to: str, subject: str, body: str, 
                        cc: Optional[str] = None, bcc: Optional[str] = None) -> str:
        """
        Send an email via Gmail.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: Carbon copy recipients (optional)
            bcc: Blind carbon copy recipients (optional)
            
        Returns:
            str: Success message with message ID
            
        Notes:
            - Uses MIME format for email composition
            - Base64 encoding required for Gmail API
            - Supports both plain text and HTML content
        """
        try:
            # Create MIME message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            # Add optional recipients
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Attach body (plain text for now)
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message for Gmail API
            # Gmail API expects base64-encoded MIME message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send via Gmail API
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully to {to}")
            return f"Email sent successfully. Message ID: {send_message['id']}"
            
        except HttpError as e:
            logger.error(f"HTTP error sending email: {e}")
            return f"Error sending email: {e}"
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return f"Error sending email: {e}"
    
    async def search_emails(self, query: str, max_results: int = DEFAULT_MAX_RESULTS) -> str:
        """
        Search emails using Gmail query syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results
            
        Returns:
            str: JSON-formatted search results
            
        Gmail Query Examples:
            - "from:sender@example.com" (from specific sender)
            - "subject:meeting" (subject contains meeting)
            - "is:unread" (unread messages)
            - "has:attachment" (has attachments)
            - "after:2023/12/01" (after specific date)
            - "label:important" (has important label)
        """
        try:
            # Search using Gmail's query syntax
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            search_data = []
            
            # Get metadata for each found message
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                # Extract headers
                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                
                search_data.append({
                    'id': message['id'],
                    'thread_id': message['threadId'],
                    'from': headers.get('From', 'Unknown'),
                    'to': headers.get('To', 'Unknown'),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', 'Unknown'),
                    'snippet': message.get('snippet', '')
                })
            
            logger.info(f"Found {len(search_data)} messages for query: {query}")
            return json.dumps(search_data, indent=2)
            
        except HttpError as e:
            logger.error(f"HTTP error searching emails: {e}")
            return f"Error searching emails: {e}"
    
    async def get_message(self, message_id: str) -> str:
        """
        Get a specific message with full content.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            str: JSON-formatted message details
            
        Notes:
            - Returns full message including body
            - Handles both plain text and HTML emails
            - Includes all headers and metadata
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'  # Get complete message
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            # Extract message body
            body = self.email_parser.extract_message_body(message['payload'])
            
            # Get message labels
            label_ids = message.get('labelIds', [])
            
            message_data = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', 'Unknown'),
                'cc': headers.get('Cc', ''),
                'bcc': headers.get('Bcc', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', 'Unknown'),
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': label_ids,
                'size_estimate': message.get('sizeEstimate', 0)
            }
            
            logger.info(f"Retrieved message: {message_id}")
            return json.dumps(message_data, indent=2)
            
        except HttpError as e:
            logger.error(f"HTTP error getting message {message_id}: {e}")
            return f"Error getting message: {e}"
    
    async def mark_as_read(self, message_id: str) -> str:
        """
        Mark a message as read by removing UNREAD label.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            str: Success or error message
            
        Notes:
            - Gmail uses labels for message states
            - UNREAD label indicates unread messages
            - Removing UNREAD label marks message as read
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info(f"Message {message_id} marked as read")
            return f"Message {message_id} marked as read"
            
        except HttpError as e:
            logger.error(f"HTTP error marking message as read: {e}")
            return f"Error marking message as read: {e}"
    
    async def add_label(self, message_id: str, label: str) -> str:
        """
        Add a label to a message.
        
        Args:
            message_id: Gmail message ID
            label: Label name to add
            
        Returns:
            str: Success or error message
            
        Notes:
            - Labels must already exist in Gmail
            - Label names are case-insensitive
            - System labels (INBOX, SENT) can also be added
        """
        try:
            # Get all labels to find the label ID
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            # Find label by name (case-insensitive)
            for lbl in labels.get('labels', []):
                if lbl['name'].lower() == label.lower():
                    label_id = lbl['id']
                    break
            
            if not label_id:
                return f"Label '{label}' not found"
            
            # Add label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            logger.info(f"Label '{label}' added to message {message_id}")
            return f"Label '{label}' added to message {message_id}"
            
        except HttpError as e:
            logger.error(f"HTTP error adding label: {e}")
            return f"Error adding label: {e}"
    
    async def remove_label(self, message_id: str, label: str) -> str:
        """
        Remove a label from a message.
        
        Args:
            message_id: Gmail message ID
            label: Label name to remove
            
        Returns:
            str: Success or error message
        """
        try:
            # Get all labels to find the label ID
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            for lbl in labels.get('labels', []):
                if lbl['name'].lower() == label.lower():
                    label_id = lbl['id']
                    break
            
            if not label_id:
                return f"Label '{label}' not found"
            
            # Remove label from message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            
            logger.info(f"Label '{label}' removed from message {message_id}")
            return f"Label '{label}' removed from message {message_id}"
            
        except HttpError as e:
            logger.error(f"HTTP error removing label: {e}")
            return f"Error removing label: {e}"
    
    async def get_thread(self, thread_id: str) -> str:
        """
        Get all messages in a thread (conversation).
        
        Args:
            thread_id: Gmail thread ID
            
        Returns:
            str: JSON-formatted thread with all messages
            
        Notes:
            - Threads group related messages together
            - Useful for getting entire conversation history
        """
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = thread.get('messages', [])
            thread_data = {
                'id': thread['id'],
                'snippet': thread.get('snippet', ''),
                'messages': []
            }
            
            # Process each message in the thread
            for message in messages:
                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                body = self.email_parser.extract_message_body(message['payload'])
                
                thread_data['messages'].append({
                    'id': message['id'],
                    'from': headers.get('From', 'Unknown'),
                    'to': headers.get('To', 'Unknown'),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', 'Unknown'),
                    'body': body,
                    'snippet': message.get('snippet', '')
                })
            
            logger.info(f"Retrieved thread {thread_id} with {len(messages)} messages")
            return json.dumps(thread_data, indent=2)
            
        except HttpError as e:
            logger.error(f"HTTP error getting thread: {e}")
            return f"Error getting thread: {e}"