"""
Secrets-based Authentication Provider (MVP Implementation).

This provider loads users from secrets.toml and uses bcrypt for password hashing.
Suitable for small teams (5-20 users) with controlled access.
"""

import streamlit as st
import bcrypt
from typing import Dict, Optional
import logging
from . import AuthenticationProvider, UserInfo

logger = logging.getLogger(__name__)


class SecretsAuthProvider(AuthenticationProvider):
    """
    Authentication provider using secrets.toml (MVP implementation).
    
    Features:
    - bcrypt password hashing with automatic salting
    - User role management (admin, trader, viewer)
    - User enable/disable without deletion
    - Comprehensive logging
    """
    
    def __init__(self):
        self._user_cache = None
        self._cache_timestamp = None
    
    def _load_users(self) -> Dict[str, Dict]:
        """
        Load users from secrets.toml with caching.
        
        Returns:
            Dict mapping email (lowercase) to user data
        """
        try:
            users = {}
            
            # Load from different role sections
            for role_section in ['admin', 'traders', 'viewers']:
                role_users = st.secrets.get('users', {}).get(role_section, {})
                for email, user_data in role_users.items():
                    users[email.lower()] = {
                        'name': user_data.get('name', 'Unknown'),
                        'password_hash': user_data.get('password_hash', ''),
                        'role': user_data.get('role', 'viewer'),
                        'enabled': user_data.get('enabled', True),
                        'email': email
                    }
            
            logger.info(f"Loaded {len(users)} users from secrets.toml")
            return users
            
        except Exception as e:
            logger.error(f"Failed to load users from secrets.toml: {e}")
            return {}
    
    def authenticate(self, email: str, password: str) -> Optional[UserInfo]:
        """
        Authenticate user with bcrypt password verification.
        
        Args:
            email: User email address
            password: Plain text password
        
        Returns:
            UserInfo if authentication successful, None otherwise
        """
        if not email or not password:
            logger.warning("Authentication attempted with empty credentials")
            return None
        
        email = email.lower().strip()
        users = self._load_users()
        
        if email not in users:
            logger.warning(f"Authentication failed: User not found - {email}")
            self.on_login_failure(email, "user_not_found")
            return None
        
        user = users[email]
        
        # Check if user is enabled
        if not user.get('enabled', True):
            logger.warning(f"Authentication failed: User disabled - {email}")
            self.on_login_failure(email, "user_disabled")
            return None
        
        # Verify password with bcrypt
        try:
            password_hash = user['password_hash']
            if password_hash.startswith('$2b$'):  # bcrypt format
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    user_info = UserInfo(
                        email=email,
                        name=user['name'],
                        role=user['role'],
                        user_id=email,
                        metadata={'auth_provider': 'secrets'}
                    )
                    logger.info(f"Authentication successful: {email}")
                    self.on_login_success(user_info)
                    return user_info
            else:
                logger.error(f"Invalid password hash format for user: {email}")
        
        except Exception as e:
            logger.error(f"Password verification error for {email}: {e}")
        
        self.on_login_failure(email, "invalid_password")
        return None
    
    def get_user_info(self, email: str) -> Optional[UserInfo]:
        """
        Get user information without authentication.
        
        Args:
            email: User email address
        
        Returns:
            UserInfo if user exists, None otherwise
        """
        email = email.lower().strip()
        users = self._load_users()
        
        if email not in users:
            return None
        
        user = users[email]
        return UserInfo(
            email=email,
            name=user['name'],
            role=user['role'],
            user_id=email,
            metadata={'auth_provider': 'secrets'}
        )
    
    def validate_user(self, email: str) -> bool:
        """
        Check if user exists and is enabled.
        
        Args:
            email: User email address
        
        Returns:
            True if user exists and is enabled, False otherwise
        """
        email = email.lower().strip()
        users = self._load_users()
        
        if email not in users:
            return False
        
        return users[email].get('enabled', True)
    
    def on_login_success(self, user: UserInfo):
        """Log successful authentication"""
        logger.info(f"✓ Login success: {user.email} ({user.role})")
    
    def on_login_failure(self, email: str, reason: str):
        """Log failed authentication"""
        logger.warning(f"✗ Login failed: {email} - Reason: {reason}")

