"""
Authentication Provider Interface for Trading Sheet Application.

This module defines the abstract base class that all authentication
providers must implement, enabling seamless swapping of auth backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass, field

@dataclass
class UserInfo:
    """Standard user information structure across all auth providers"""
    email: str
    name: str
    role: str
    user_id: Optional[str] = None
    metadata: Optional[Dict] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for session storage"""
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'user_id': self.user_id,
            'metadata': self.metadata or {}
        }


class AuthenticationProvider(ABC):
    """
    Abstract authentication provider interface.
    
    ALL authentication providers must implement these methods.
    This allows swapping auth implementations without changing app code.
    
    Examples:
        - SecretsAuthProvider: secrets.toml based (MVP)
        - OAuth2AuthProvider: Google/Microsoft SSO (future)
        - LDAPAuthProvider: Active Directory (future)
        - DatabaseAuthProvider: PostgreSQL/MySQL (future)
    """
    
    @abstractmethod
    def authenticate(self, email: str, password: str) -> Optional[UserInfo]:
        """
        Authenticate user with credentials.
        
        Args:
            email: User email address
            password: Plain text password
        
        Returns:
            UserInfo if authentication successful, None otherwise
        """
        pass
    
    @abstractmethod
    def get_user_info(self, email: str) -> Optional[UserInfo]:
        """
        Retrieve user information by email (without authentication).
        
        Args:
            email: User email address
        
        Returns:
            UserInfo if user exists, None otherwise
        """
        pass
    
    @abstractmethod
    def validate_user(self, email: str) -> bool:
        """
        Check if user exists and is enabled.
        
        Args:
            email: User email address
        
        Returns:
            True if user valid and enabled, False otherwise
        """
        pass
    
    def on_login_success(self, user: UserInfo):
        """Hook for post-login actions (logging, metrics, etc.)"""
        pass
    
    def on_login_failure(self, email: str, reason: str):
        """Hook for failed login actions (logging, rate limiting, etc.)"""
        pass

