"""
Gmail MCP Server - Data Models and Schemas
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class EmailMessage:
    """Represents a Gmail message"""
    id: str
    thread_id: str
    from_email: str
    to_email: str
    subject: str
    date: str
    body: str
    snippet: str
    labels: List[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class EmailMessageSummary:
    """Represents a summary of a Gmail message (for lists)"""
    id: str
    from_email: str
    to_email: str
    subject: str
    date: str
    snippet: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class GmailLabel:
    """Represents a Gmail label"""
    id: str
    name: str
    type: str
    messages_total: Optional[int] = None
    messages_unread: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class EmailSendRequest:
    """Represents an email send request"""
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate required fields"""
        return bool(self.to and self.subject and self.body)


@dataclass
class EmailSearchRequest:
    """Represents an email search request"""
    query: str
    max_results: int = 10
    
    def validate(self) -> bool:
        """Validate search request"""
        return bool(self.query and self.max_results > 0)


@dataclass
class ToolResponse:
    """Represents a tool execution response"""
    success: bool
    message: str
    data: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ResourceData:
    """Represents MCP resource data"""
    uri: str
    name: str
    description: str
    mime_type: str
    content: Any
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class GmailMessageBuilder:
    """Builder class for creating EmailMessage objects from Gmail API responses"""
    
    @staticmethod
    def from_gmail_message(gmail_message: Dict[str, Any]) -> EmailMessage:
        """Create EmailMessage from Gmail API message response"""
        headers = {
            h['name']: h['value'] 
            for h in gmail_message['payload'].get('headers', [])
        }
        
        return EmailMessage(
            id=gmail_message['id'],
            thread_id=gmail_message['threadId'],
            from_email=headers.get('From', 'Unknown'),
            to_email=headers.get('To', 'Unknown'),
            subject=headers.get('Subject', 'No Subject'),
            date=headers.get('Date', 'Unknown'),
            body='',  # Will be populated by email utils
            snippet=gmail_message.get('snippet', ''),
            labels=gmail_message.get('labelIds', [])
        )
    
    @staticmethod
    def from_gmail_message_summary(gmail_message: Dict[str, Any]) -> EmailMessageSummary:
        """Create EmailMessageSummary from Gmail API message response"""
        headers = {
            h['name']: h['value'] 
            for h in gmail_message['payload'].get('headers', [])
        }
        
        return EmailMessageSummary(
            id=gmail_message['id'],
            from_email=headers.get('From', 'Unknown'),
            to_email=headers.get('To', 'Unknown'),
            subject=headers.get('Subject', 'No Subject'),
            date=headers.get('Date', 'Unknown'),
            snippet=gmail_message.get('snippet', '')
        )


class GmailLabelBuilder:
    """Builder class for creating GmailLabel objects from Gmail API responses"""
    
    @staticmethod
    def from_gmail_label(gmail_label: Dict[str, Any]) -> GmailLabel:
        """Create GmailLabel from Gmail API label response"""
        return GmailLabel(
            id=gmail_label['id'],
            name=gmail_label['name'],
            type=gmail_label.get('type', 'user'),
            messages_total=gmail_label.get('messagesTotal'),
            messages_unread=gmail_label.get('messagesUnread')
        )


# Type aliases for better code readability
MessageList = List[EmailMessage]
MessageSummaryList = List[EmailMessageSummary]
LabelList = List[GmailLabel]