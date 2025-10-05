"""
Authentication Manager for Trading Sheet Application.

This module provides authentication services while abstracting
the underlying authentication provider. This allows seamless
migration to different auth systems (OAuth, SSO, LDAP) without
changing application code.

Usage in pages:
    from app.auth import require_auth, get_current_user
    
    require_auth()  # Add at top of page to protect it
    user = get_current_user()  # Get current user info
"""

import streamlit as st
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from collections import defaultdict

# Import providers
from app.auth_providers import AuthenticationProvider, UserInfo
from app.auth_providers.secrets import SecretsAuthProvider

logger = logging.getLogger(__name__)

# ============================================
# RATE LIMITING
# ============================================
login_attempts = defaultdict(list)  # email -> [timestamp, ...]

def _is_rate_limited(email: str) -> bool:
    """Check if user is rate limited due to too many failed attempts"""
    max_attempts = st.secrets.get('auth', {}).get('max_login_attempts', 5)
    lockout_minutes = st.secrets.get('auth', {}).get('lockout_duration_minutes', 15)
    
    # Clean old attempts
    cutoff_time = datetime.now() - timedelta(minutes=lockout_minutes)
    login_attempts[email] = [t for t in login_attempts[email] if t > cutoff_time]
    
    # Check limit
    if len(login_attempts[email]) >= max_attempts:
        logger.warning(f"Rate limit exceeded for {email}")
        return True
    
    return False

def _record_login_attempt(email: str):
    """Record a login attempt for rate limiting"""
    login_attempts[email].append(datetime.now())

def _clear_login_attempts(email: str):
    """Clear login attempts after successful login"""
    if email in login_attempts:
        login_attempts[email] = []

# ============================================
# AUTHENTICATION PROVIDER MANAGEMENT
# ============================================
_auth_provider: Optional[AuthenticationProvider] = None

def _get_auth_provider() -> AuthenticationProvider:
    """
    Get configured authentication provider.
    
    Returns:
        Configured AuthenticationProvider instance
    """
    global _auth_provider
    
    if _auth_provider is None:
        # Determine provider from config
        provider_type = st.secrets.get('auth', {}).get('provider', 'secrets')
        
        if provider_type == 'secrets':
            _auth_provider = SecretsAuthProvider()
        # elif provider_type == 'oauth':
        #     _auth_provider = OAuth2AuthProvider()  # Future
        # elif provider_type == 'ldap':
        #     _auth_provider = LDAPAuthProvider()  # Future
        else:
            logger.error(f"Unknown provider: {provider_type}, defaulting to secrets")
            _auth_provider = SecretsAuthProvider()
    
    return _auth_provider

def set_auth_provider(provider: AuthenticationProvider):
    """
    Set custom authentication provider.
    
    Useful for testing or custom implementations.
    
    Args:
        provider: AuthenticationProvider instance
    """
    global _auth_provider
    _auth_provider = provider
    logger.info(f"Authentication provider set to: {provider.__class__.__name__}")

# ============================================
# SESSION MANAGEMENT
# ============================================
def _create_session(user: UserInfo):
    """
    Create authenticated session in Streamlit session state.
    
    Args:
        user: UserInfo object with user details
    """
    session_id = str(uuid.uuid4())
    
    st.session_state['auth_user'] = user.to_dict()
    st.session_state['auth_session_id'] = session_id
    st.session_state['auth_login_time'] = datetime.now().isoformat()
    st.session_state['auth_last_activity'] = datetime.now().isoformat()
    st.session_state['auth_provider'] = user.metadata.get('auth_provider', 'unknown')
    
    logger.info(f"Session created: {session_id} for {user.email}")

def _update_activity():
    """Update last activity timestamp"""
    if is_authenticated():
        st.session_state['auth_last_activity'] = datetime.now().isoformat()

def _validate_session() -> bool:
    """
    Validate current session (check timeouts).
    
    Returns:
        True if session is valid, False if expired
    """
    if not is_authenticated():
        return False
    
    # Check session timeout (absolute)
    timeout_minutes = st.secrets.get('auth', {}).get('session_timeout_minutes', 60)
    login_time = datetime.fromisoformat(st.session_state['auth_login_time'])
    
    if datetime.now() - login_time > timedelta(minutes=timeout_minutes):
        logger.info("Session expired (absolute timeout)")
        logout()
        return False
    
    # Check inactivity timeout
    inactivity_minutes = st.secrets.get('auth', {}).get('session_inactivity_timeout_minutes', 30)
    last_activity = datetime.fromisoformat(st.session_state['auth_last_activity'])
    
    if datetime.now() - last_activity > timedelta(minutes=inactivity_minutes):
        logger.info("Session expired (inactivity timeout)")
        logout()
        return False
    
    _update_activity()
    return True

# ============================================
# PUBLIC API
# ============================================
def authenticate(email: str, password: str) -> bool:
    """
    Authenticate user with credentials.
    
    Args:
        email: User email address
        password: Plain text password
    
    Returns:
        True if authentication successful, False otherwise
    """
    # Check rate limiting
    if _is_rate_limited(email):
        logger.warning(f"Authentication blocked (rate limit): {email}")
        return False
    
    # Record attempt
    _record_login_attempt(email)
    
    # Authenticate with provider
    provider = _get_auth_provider()
    user = provider.authenticate(email, password)
    
    if user:
        _create_session(user)
        _clear_login_attempts(email)  # Clear failed attempts on success
        return True
    
    return False

def is_authenticated() -> bool:
    """
    Check if current session is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    return 'auth_user' in st.session_state and 'auth_session_id' in st.session_state

def get_current_user() -> Optional[Dict]:
    """
    Get current authenticated user's information.
    
    Returns:
        Dict with user info or None if not authenticated
    """
    if not is_authenticated() or not _validate_session():
        return None
    
    return st.session_state['auth_user']

def logout():
    """Clear session state and logout user"""
    email = st.session_state.get('auth_user', {}).get('email', 'unknown')
    logger.info(f"Logout: {email}")
    
    keys_to_clear = [
        'auth_user', 'auth_session_id', 'auth_login_time', 
        'auth_last_activity', 'auth_provider'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def require_auth(allowed_roles: Optional[List[str]] = None):
    """
    Protect page - redirect to login if not authenticated.
    
    Usage:
        from app.auth import require_auth
        require_auth()  # All authenticated users
        require_auth(['admin', 'trader'])  # Specific roles only
    
    Args:
        allowed_roles: List of roles allowed (None = all authenticated users)
    """
    # Validate session
    if not is_authenticated() or not _validate_session():
        st.warning("⚿ Please login to access this page")
        st.stop()
    
    # Check role-based access
    if allowed_roles:
        user = get_current_user()
        if user and user.get('role') not in allowed_roles:
            st.error("⚠ You don't have permission to access this page")
            st.stop()

def get_user_info(email: str) -> Optional[Dict]:
    """
    Get user information by email (without authentication).
    
    Args:
        email: User email address
    
    Returns:
        Dict with user info or None if not found
    """
    provider = _get_auth_provider()
    user = provider.get_user_info(email)
    return user.to_dict() if user else None

def get_remaining_lockout_time(email: str) -> Optional[int]:
    """
    Get remaining lockout time in seconds for rate-limited user.
    
    Args:
        email: User email address
    
    Returns:
        Seconds remaining in lockout, or None if not locked out
    """
    if not _is_rate_limited(email):
        return None
    
    lockout_minutes = st.secrets.get('auth', {}).get('lockout_duration_minutes', 15)
    if email in login_attempts and login_attempts[email]:
        oldest_attempt = min(login_attempts[email])
        lockout_end = oldest_attempt + timedelta(minutes=lockout_minutes)
        remaining = (lockout_end - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    return None

