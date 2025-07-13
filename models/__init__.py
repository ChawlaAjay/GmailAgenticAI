"""
Gmail MCP Server - Models Package
"""

from .gmail_models import (
    EmailMessage,
    EmailMessageSummary,
    GmailLabel,
    EmailSendRequest,
    EmailSearchRequest,
    ToolResponse,
    ResourceData,
    GmailMessageBuilder,
    GmailLabelBuilder,
    MessageList,
    MessageSummaryList,
    LabelList
)

__all__ = [
    'EmailMessage',
    'EmailMessageSummary',
    'GmailLabel',
    'EmailSendRequest',
    'EmailSearchRequest',
    'ToolResponse',
    'ResourceData',
    'GmailMessageBuilder',
    'GmailLabelBuilder',
    'MessageList',
    'MessageSummaryList',
    'LabelList'
]