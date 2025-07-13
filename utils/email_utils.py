"""
Email Parsing Utilities
========================

This module provides utilities for parsing Gmail message data.
Gmail messages can have complex structures with multiple parts,
encodings, and content types.

Key Email Concepts:
- MIME: Multipurpose Internet Mail Extensions
- Parts: Email sections (text, HTML, attachments)
- Encoding: How binary data is represented (base64, quoted-printable)
- Content Types: text/plain, text/html, multipart/mixed, etc.
"""

import base64
import logging
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailParser:
    """
    Utilities for parsing Gmail message data.
    
    This class handles:
    - Extracting message body from complex MIME structures
    - Decoding base64 and other encodings
    - Handling multipart messages
    - Extracting attachments info
    """
    
    def extract_message_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract message body from Gmail payload.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            str: Extracted message body
            
        Notes:
            - Gmail messages can have complex nested structures
            - Handles both simple and multipart messages
            - Prefers plain text over HTML when both available
        """
        try:
            # Check if message has multiple parts
            if 'parts' in payload:
                return self._extract_from_parts(payload['parts'])
            else:
                # Single part message
                return self._extract_from_single_part(payload)
                
        except Exception as e:
            logger.error(f"Error extracting message body: {e}")
            return f"Error extracting message body: {e}"
    
    def _extract_from_parts(self, parts: List[Dict[str, Any]]) -> str:
        """
        Extract body from multipart message.
        
        Args:
            parts: List of message parts
            
        Returns:
            str: Extracted body text
            
        Notes:
            - Multipart messages can contain text, HTML, and attachments
            - Priority: text/plain > text/html > other types
            - Recursively handles nested parts
        """
        plain_text = ""
        html_text = ""
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            
            # Handle nested parts (multipart/alternative, etc.)
            if 'parts' in part:
                nested_body = self._extract_from_parts(part['parts'])
                if nested_body:
                    return nested_body
            
            # Extract text content
            elif mime_type == 'text/plain':
                plain_text = self._decode_message_data(part)
            elif mime_type == 'text/html':
                html_text = self._decode_message_data(part)
        
        # Prefer plain text over HTML
        return plain_text if plain_text else html_text
    
    def _extract_from_single_part(self, payload: Dict[str, Any]) -> str:
        """
        Extract body from single part message.
        
        Args:
            payload: Message payload
            
        Returns:
            str: Extracted body text
        """
        mime_type = payload.get('mimeType', '')
        
        if mime_type in ['text/plain', 'text/html']:
            return self._decode_message_data(payload)
        
        return f"Unsupported content type: {mime_type}"
    
    def _decode_message_data(self, part: Dict[str, Any]) -> str:
        """
        Decode base64 encoded message data.
        
        Args:
            part: Message part containing encoded data
            
        Returns:
            str: Decoded message content
            
        Notes:
            - Gmail API returns message content as base64-encoded
            - Uses URL-safe base64 encoding
            - Handles encoding errors gracefully
        """
        try:
            body = part.get('body', {})
            data = body.get('data', '')
            
            if not data:
                return ""
            
            # Decode base64 data
            decoded_bytes = base64.urlsafe_b64decode(data)
            
            # Convert to string (UTF-8 encoding)
            return decoded_bytes.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error decoding message data: {e}")
            return f"Error decoding message data: {e}"
    
    def extract_attachments_info(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract attachment information from message.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            List[Dict]: List of attachment info dictionaries
            
        Notes:
            - Returns metadata about attachments, not the actual files
            - Includes filename, size, and content type
            - Actual attachment download requires separate API call
        """
        attachments = []
        
        try:
            if 'parts' in payload:
                self._find_attachments_in_parts(payload['parts'], attachments)
            else:
                # Check if single part is an attachment
                if self._is_attachment(payload):
                    attachments.append(self._extract_attachment_info(payload))
                    
        except Exception as e:
            logger.error(f"Error extracting attachments: {e}")
        
        return attachments
    
    def _find_attachments_in_parts(self, parts: List[Dict[str, Any]], 
                                  attachments: List[Dict[str, Any]]):
        """
        Recursively find attachments in message parts.
        
        Args:
            parts: List of message parts
            attachments: List to append found attachments
        """
        for part in parts:
            # Check for nested parts
            if 'parts' in part:
                self._find_attachments_in_parts(part['parts'], attachments)
            elif self._is_attachment(part):
                attachments.append(self._extract_attachment_info(part))
    
    def _is_attachment(self, part: Dict[str, Any]) -> bool:
        """
        Check if a message part is an attachment.
        
        Args:
            part: Message part
            
        Returns:
            bool: True if part is an attachment
        """
        body = part.get('body', {})
        headers = part.get('headers', [])
        
        # Check for attachment ID (indicates downloadable attachment)
        if body.get('attachmentId'):
            return True
        
        # Check Content-Disposition header
        for header in headers:
            if header.get('name', '').lower() == 'content-disposition':
                if 'attachment' in header.get('value', '').lower():
                    return True
        
        return False
    
    def _extract_attachment_info(self, part: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract attachment information from message part.
        
        Args:
            part: Message part
            
        Returns:
            Dict: Attachment information
        """
        body = part.get('body', {})
        headers = part.get('headers', [])
        
        # Extract filename from headers
        filename = "unknown"
        for header in headers:
            if header.get('name', '').lower() == 'content-disposition':
                value = header.get('value', '')
                if 'filename=' in value:
                    filename = value.split('filename=')[1].strip('"')
                    break
        
        return {
            'filename': filename,
            'mime_type': part.get('mimeType', 'unknown'),
            'size': body.get('size', 0),
            'attachment_id': body.get('attachmentId', '')
        }
    
    def clean_email_address(self, email_str: str) -> str:
        """
        Clean and extract email address from Gmail format.
        
        Args:
            email_str: Email string from Gmail (e.g., "John Doe <john@example.com>")
            
        Returns:
            str: Clean email address
            
        Examples:
            "John Doe <john@example.com>" -> "john@example.com"
            "john@example.com" -> "john@example.com"
        """
        if not email_str:
            return ""
        
        # Extract email from "Name <email>" format
        if '<' in email_str and '>' in email_str:
            start = email_str.find('<') + 1
            end = email_str.find('>')
            return email_str[start:end].strip()
        
        return email_str.strip()
    
    def parse_email_list(self, email_list_str: str) -> List[str]:
        """
        Parse comma-separated email list.
        
        Args:
            email_list_str: Comma-separated email addresses
            
        Returns:
            List[str]: List of clean email addresses
        """
        if not email_list_str:
            return []
        
        emails = []
        for email in email_list_str.split(','):
            clean_email = self.clean_email_address(email)
            if clean_email:
                emails.append(clean_email)
        
        return emails
    
    def extract_reply_to(self, headers: List[Dict[str, str]]) -> Optional[str]:
        """
        Extract Reply-To header from message headers.
        
        Args:
            headers: List of message headers
            
        Returns:
            Optional[str]: Reply-To address if present
        """
        for header in headers:
            if header.get('name', '').lower() == 'reply-to':
                return self.clean_email_address(header.get('value', ''))
        
        return None
    
    def get_message_priority(self, headers: List[Dict[str, str]]) -> str:
        """
        Get message priority from headers.
        
        Args:
            headers: List of message headers
            
        Returns:
            str: Priority level (high, normal, low)
        """
        priority_headers = ['x-priority', 'priority', 'importance']
        
        for header in headers:
            header_name = header.get('name', '').lower()
            if header_name in priority_headers:
                value = header.get('value', '').lower()
                if '1' in value or 'high' in value:
                    return 'high'
                elif '5' in value or 'low' in value:
                    return 'low'
        
        return 'normal'


class EmailBuilder:
    """
    Utility class for building email messages.
    """
    
    def create_message(self, to: str, subject: str, body: str, 
                      cc: str = None, bcc: str = None) -> MIMEMultipart:
        """
        Create a MIME message for sending.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            
        Returns:
            MIMEMultipart: Formatted email message
        """
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        message.attach(MIMEText(body, 'plain'))
        return message


# Convenience functions for backward compatibility
def extract_message_body(payload: Dict[str, Any]) -> str:
    """
    Extract message body from Gmail payload.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        str: Extracted message body
    """
    parser = EmailParser()
    return parser.extract_message_body(payload)


def create_message(to: str, subject: str, body: str, 
                  cc: str = None, bcc: str = None) -> MIMEMultipart:
    """
    Create a MIME message for sending.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        
    Returns:
        MIMEMultipart: Formatted email message
    """
    builder = EmailBuilder()
    return builder.create_message(to, subject, body, cc, bcc)