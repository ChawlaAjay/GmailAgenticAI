"""
Gmail Authentication Handler
============================

This module handles OAuth2 authentication with Gmail API.
It manages the entire authentication flow including:
- Initial OAuth setup
- Token refresh
- Credential storage
- Service building

OAuth2 Flow Explained:
1. User runs app for first time
2. Browser opens for Google login
3. User grants permissions
4. Google returns authorization code
5. App exchanges code for tokens
6. Tokens are saved for future use
7. On subsequent runs, saved tokens are used
8. If tokens expire, they're automatically refreshed
"""

import os
import logging
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import SCOPES, CREDENTIALS_FILE, TOKEN_FILE, DEFAULT_PORT

logger = logging.getLogger(__name__)

class GmailAuthenticator:
    """
    Handles Gmail API authentication using OAuth2.
    
    This class manages the complete authentication lifecycle:
    - Initial user authorization
    - Token storage and retrieval
    - Automatic token refresh
    - Gmail service creation
    """
    
    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.service = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Flow:
        1. Try to load existing credentials from token file
        2. If no valid credentials, start OAuth flow
        3. If credentials expired, refresh them
        4. Save updated credentials
        5. Build Gmail service
        """
        try:
            self.credentials = self._load_credentials()
            
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing expired credentials...")
                    self._refresh_credentials()
                else:
                    logger.info("Starting OAuth flow...")
                    self._run_oauth_flow()
                
                self._save_credentials()
            
            self.service = self._build_service()
            logger.info("Gmail authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def _load_credentials(self) -> Optional[Credentials]:
        """
        Load credentials from token file if it exists.
        
        Returns:
            Optional[Credentials]: Loaded credentials or None
            
        Notes:
            - Token file is created after first successful OAuth
            - Contains access token, refresh token, and metadata
        """
        if TOKEN_FILE.exists():
            logger.info("Loading existing credentials...")
            return Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        return None
    
    def _refresh_credentials(self):
        """
        Refresh expired credentials using refresh token.
        
        Notes:
            - Refresh tokens are long-lived (usually don't expire)
            - Access tokens are short-lived (usually 1 hour)
            - This method gets new access token without user interaction
        """
        self.credentials.refresh(Request())
        logger.info("Credentials refreshed successfully")
    
    def _run_oauth_flow(self):
        """
        Run the OAuth2 authorization flow.
        
        This method:
        1. Starts local server for OAuth callback
        2. Opens browser for user login
        3. Handles the authorization response
        4. Exchanges authorization code for tokens
        
        Notes:
            - Only runs on first setup or if refresh token invalid
            - Requires user interaction (browser login)
            - Uses 'Desktop application' OAuth flow
        """
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), 
            SCOPES
        )
        
        # Run local server for OAuth callback
        # Port 0 means "choose any available port"
        self.credentials = flow.run_local_server(port=DEFAULT_PORT)
        logger.info("OAuth flow completed successfully")
    
    def _save_credentials(self):
        """
        Save credentials to token file for future use.
        
        Notes:
            - Creates token file if it doesn't exist
            - Overwrites existing token file
            - Token file should be kept secure and private
        """
        # Ensure auth directory exists
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(self.credentials.to_json())
        logger.info("Credentials saved to token file")
    
    def _build_service(self):
        """
        Build Gmail API service object.
        
        Returns:
            Gmail service object for making API calls
            
        Notes:
            - Service object is used for all Gmail API operations
            - Version 'v1' is the current stable Gmail API version
            - Service handles authentication automatically
        """
        try:
            service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail service built successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            raise
    
    def get_service(self):
        """
        Get the authenticated Gmail service.
        
        Returns:
            Gmail service object
            
        Raises:
            Exception: If not authenticated
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")
        return self.service
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            bool: True if authenticated and service is available
        """
        return self.service is not None and self.credentials is not None