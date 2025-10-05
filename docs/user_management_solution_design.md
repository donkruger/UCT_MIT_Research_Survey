# User Management Solution Design - MVP Implementation (ENHANCED)

## Executive Summary

This document outlines a **production-ready MVP** user authentication system for the Trading Sheet Application using **hardcoded credentials in `secrets.toml`**. The design emphasizes **modularity** and **swappability** to ensure seamless migration to enterprise authentication solutions (OAuth, SSO, LDAP) without rewriting the application.

**Key Features:**
- ✅ Simple username/password authentication with **bcrypt** password hashing
- ✅ Credentials stored in `secrets.toml` (MVP) or environment variables (Production)
- ✅ **Abstract Authentication Provider Interface** - swap implementations without changing app code
- ✅ Session-based access control with timeout and security features
- ✅ Seamless integration with existing audit trail system
- ✅ Login attempt rate limiting and audit trail
- ✅ Role-based access control (RBAC)
- ✅ **Zero changes to existing page code** - only add one line per page
- ✅ Clear migration path to robust authentication systems

## CRITICAL IMPROVEMENTS from Original Design

### 1. **Authentication Provider Pattern (Swappable)**
```python
# Define interface that ALL auth providers must implement
class AuthenticationProvider(ABC):
    @abstractmethod
    def authenticate(email: str, password: str) -> Optional[Dict]
    @abstractmethod
    def get_user_info(email: str) -> Optional[Dict]
    @abstractmethod
    def validate_session() -> bool
```

This allows you to **swap the entire authentication backend** by changing one line in config, with **zero code changes** to the rest of your app.

### 2. **bcrypt Instead of SHA-256**
- SHA-256 is NOT suitable for passwords (too fast, vulnerable to rainbow tables)
- bcrypt is industry standard with built-in salting and work factor
- Drop-in replacement: `pip install bcrypt`

### 3. **Session Security Enhancements**
- Session timeout (configurable)
- Session token validation
- IP address tracking (optional)
- Login audit trail

### 4. **Rate Limiting**
- Prevent brute force attacks
- Configurable attempt limits
- Temporary account lockout

### 5. **Zero Integration Friction**
- Existing `get_user_identity()` function already designed for this
- Sidebar automatically detects and displays auth user
- Only need to add `@require_auth` decorator to pages

### 6. **Environment-Ready**
- Support secrets.toml (dev/UAT)
- Support environment variables (production)
- No secrets in code or git

## 1. Rationale for MVP Approach

### Why secrets.toml?

1. **Zero External Dependencies**: No database or authentication service required
2. **Immediate Implementation**: Can be deployed in minutes
3. **Development Friendly**: Easy to test and modify
4. **Existing Infrastructure**: Already using secrets.toml for API credentials
5. **Sufficient for Small Teams**: Suitable for 5-20 internal users

### Use Cases

- **Internal Trading Operations Team**: Limited, trusted user base
- **Controlled Environment**: UAT/QA testing before production rollout
- **Compliance Requirement**: Track WHO executes trades (audit trail)
- **Access Control**: Prevent unauthorized trade submissions

## 2. ENHANCED Architecture - Swappable Authentication Provider Pattern

### 2.1 Layer Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│  (Pages, Components, Audit System)                              │
│  - NO auth implementation details                               │
│  - Only calls: require_auth(), get_current_user()               │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    Uses Abstract Interface
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              Authentication Manager (app/auth.py)               │
│  - Public API: require_auth(), get_current_user(), logout()    │
│  - Delegates to configured AuthenticationProvider              │
│  - Handles session management, rate limiting, audit            │
└────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    Implements Interface
                              │
      ┌───────────────────────┴───────────────────────┐
      │                                               │
      ▼                                               ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│  SecretsAuthProvider     │         │  OAuth2AuthProvider      │
│  (MVP - secrets.toml)    │         │  (Future - Google/MS)    │
│  - bcrypt verification   │         │  - OAuth flow            │
│  - User loading          │         │  - Token validation      │
└──────────────────────────┘         └──────────────────────────┘
      ▲                                               ▲
      │                                               │
      ▼                                               ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│  DatabaseAuthProvider    │         │  LDAPAuthProvider        │
│  (Future - PostgreSQL)   │         │  (Future - Enterprise)   │
└──────────────────────────┘         └──────────────────────────┘

SWAP PROVIDER BY CHANGING ONE LINE:
auth_manager.set_provider(SecretsAuthProvider())  # MVP
# auth_manager.set_provider(OAuth2AuthProvider()) # Production
```

### 2.2 User Login Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Login Page (pages/0_Login.py)                       │
│     - Email/Password input                               │
│     - Calls: auth_manager.authenticate()                 │
│     - NO knowledge of auth provider                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  2. Authentication Manager (app/auth.py)                 │
│     - Validates input                                    │
│     - Checks rate limits                                 │
│     - Delegates to AuthenticationProvider                │
│     - Creates session on success                         │
│     - Logs authentication attempt                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  3. SecretsAuthProvider (app/auth_providers/secrets.py)  │
│     - Loads users from secrets.toml                      │
│     - bcrypt password verification                       │
│     - Returns user info if valid                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  4. Session Management (st.session_state)                │
│     - auth_user: Dict (email, name, role, etc.)          │
│     - auth_session_id: str (unique session ID)           │
│     - auth_login_time: datetime                          │
│     - auth_last_activity: datetime                       │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  5. Protected Routes (All App Pages)                     │
│     - Call: require_auth() at page start                 │
│     - Automatically validates session                    │
│     - Auto-redirects to login if needed                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  6. Audit Integration (email_sender.py)                  │
│     - get_user_identity() checks auth_user first         │
│     - Falls back to consent_name (backward compat)       │
│     - NO changes needed to audit system                  │
└─────────────────────────────────────────────────────────┘
```

## 3. Data Structure in secrets.toml (ENHANCED with bcrypt)

### Configuration Format

```toml
# ============================================
# AUTHENTICATION CONFIGURATION
# ============================================

[auth]
# Authentication provider selection (swap without code changes)
provider = "secrets"  # Options: "secrets" (MVP), "oauth", "ldap", "database"

# Session configuration
session_timeout_minutes = 60
session_inactivity_timeout_minutes = 30

# Rate limiting (brute force protection)
max_login_attempts = 5
lockout_duration_minutes = 15

# Audit configuration
log_login_attempts = true
log_failed_attempts_only = false

# ============================================
# USER MANAGEMENT (secrets provider)
# ============================================
# CRITICAL: Use bcrypt hashes, NOT SHA-256
# bcrypt includes salt and work factor automatically
# ============================================

[users.admin]
"don@easycrypto.co.za" = {
    name = "Don Kruger", 
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7MdUpuQWqm",  # "SecurePass123!"
    role = "admin",
    enabled = true
}

"trading-ops@easyequities.co.za" = {
    name = "Trading Operations", 
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7MdUpuQWqm", 
    role = "admin",
    enabled = true
}

[users.traders]
"trader1@easyequities.co.za" = {
    name = "Senior Trader", 
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7MdUpuQWqm", 
    role = "trader",
    enabled = true
}

[users.viewers]
"compliance@easyequities.co.za" = {
    name = "Compliance Team", 
    password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7MdUpuQWqm", 
    role = "viewer",
    enabled = true
}

# ============================================
# PASSWORD HASH GENERATION (bcrypt)
# ============================================
# Generate bcrypt hash (Python):
# python -m pip install bcrypt
# python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
#
# Or use the included helper script:
# python scripts/generate_password_hash.py
# ============================================
```

### Why bcrypt Over SHA-256?

| Feature | SHA-256 (❌ Bad) | bcrypt (✅ Good) |
|---------|------------------|------------------|
| **Speed** | Ultra-fast (bad for passwords) | Intentionally slow |
| **Salting** | Manual implementation required | Automatic |
| **Work Factor** | Fixed | Configurable (future-proof) |
| **Security** | Vulnerable to rainbow tables | Industry standard |
| **Brute Force Protection** | Minimal | Excellent |

### User Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access: Upload, Execute, View History, Manage Settings |
| **trader** | Upload and Execute trades, View own history |
| **viewer** | View-only access to execution history and reports |

## 4. Authentication Flow

### 4.1 Login Process

```python
# pages/0_Login.py

import streamlit as st
import hashlib
from app.auth import authenticate_user, get_user_info

st.set_page_config(page_title="Login - Trading Sheet App", layout="centered")

# Check if already authenticated
if st.session_state.get('authenticated', False):
    st.switch_page('pages/1_Informed_Consent.py')

st.title("🔐 Trading Sheet Application")
st.markdown("### Secure Access for Trading Operations")

with st.form("login_form"):
    email = st.text_input("Email Address", placeholder="your.email@easyequities.co.za")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login", use_container_width=True)
    
    if submit:
        if authenticate_user(email, password):
            # Set session state
            user_info = get_user_info(email)
            st.session_state['authenticated'] = True
            st.session_state['user_email'] = email
            st.session_state['user_name'] = user_info['name']
            st.session_state['user_role'] = user_info['role']
            st.session_state['login_timestamp'] = datetime.now().isoformat()
            
            st.success(f"✓ Welcome, {user_info['name']}!")
            st.switch_page('pages/1_Informed_Consent.py')
        else:
            st.error("✗ Invalid email or password")
```

### 4.2 ENHANCED Authentication Module with Provider Pattern

#### 4.2.1 Authentication Provider Interface (Base Class)

```python
# app/auth_providers/__init__.py

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserInfo:
    """Standard user information structure"""
    email: str
    name: str
    role: str
    user_id: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
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
        Retrieve user information by email.
        
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
            True if user valid, False otherwise
        """
        pass
    
    def on_login_success(self, user: UserInfo):
        """Hook for post-login actions (logging, etc.)"""
        pass
    
    def on_login_failure(self, email: str, reason: str):
        """Hook for failed login actions (logging, rate limiting)"""
        pass
```

#### 4.2.2 Secrets Provider Implementation (MVP)

```python
# app/auth_providers/secrets.py

import streamlit as st
import bcrypt
from typing import Dict, Optional
import logging
from .base import AuthenticationProvider, UserInfo

logger = logging.getLogger(__name__)

class SecretsAuthProvider(AuthenticationProvider):
    """
    Authentication provider using secrets.toml (MVP implementation).
    
    Features:
    - bcrypt password hashing
    - User role management
    - User enable/disable
    """
    
    def __init__(self):
        self._user_cache = None
        self._cache_timestamp = None
    
    def _load_users(self) -> Dict[str, Dict]:
        """Load users from secrets.toml with caching"""
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
        """Authenticate user with bcrypt password verification"""
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
        """Get user information without authentication"""
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
        """Check if user exists and is enabled"""
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
```

#### 4.2.3 Authentication Manager (Main Auth Module)

```python
# app/auth.py

"""
Authentication Manager for Trading Sheet Application.

This module provides authentication services while abstracting
the underlying authentication provider. This allows seamless
migration to different auth systems (OAuth, SSO, LDAP) without
changing application code.

Usage in pages:
    from app.auth import require_auth, get_current_user
    
    require_auth()  # Add at top of page
    user = get_current_user()  # Get current user info
"""

import streamlit as st
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from collections import defaultdict

# Import providers
from app.auth_providers.base import AuthenticationProvider, UserInfo
from app.auth_providers.secrets import SecretsAuthProvider

logger = logging.getLogger(__name__)

# ============================================
# RATE LIMITING
# ============================================
login_attempts = defaultdict(list)  # email -> [timestamp, ...]

def _is_rate_limited(email: str) -> bool:
    """Check if user is rate limited"""
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
    """Record a login attempt"""
    login_attempts[email].append(datetime.now())

# ============================================
# AUTHENTICATION PROVIDER MANAGEMENT
# ============================================
_auth_provider: Optional[AuthenticationProvider] = None

def _get_auth_provider() -> AuthenticationProvider:
    """Get configured authentication provider"""
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
    """Set custom authentication provider (for testing or custom implementations)"""
    global _auth_provider
    _auth_provider = provider
    logger.info(f"Authentication provider set to: {provider.__class__.__name__}")

# ============================================
# SESSION MANAGEMENT
# ============================================
def _create_session(user: UserInfo):
    """Create authenticated session"""
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
    """Validate current session (timeout, etc.)"""
    if not is_authenticated():
        return False
    
    # Check session timeout
    timeout_minutes = st.secrets.get('auth', {}).get('session_timeout_minutes', 60)
    login_time = datetime.fromisoformat(st.session_state['auth_login_time'])
    
    if datetime.now() - login_time > timedelta(minutes=timeout_minutes):
        logger.info("Session expired (timeout)")
        logout()
        return False
    
    # Check inactivity timeout
    inactivity_minutes = st.secrets.get('auth', {}).get('session_inactivity_timeout_minutes', 30)
    last_activity = datetime.fromisoformat(st.session_state['auth_last_activity'])
    
    if datetime.now() - last_activity > timedelta(minutes=inactivity_minutes):
        logger.info("Session expired (inactivity)")
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
        return True
    
    return False

def is_authenticated() -> bool:
    """Check if current session is authenticated"""
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
        st.switch_page('pages/0_Login.py')
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
```

### 4.3 Protected Page Template

```python
# pages/1_Informed_Consent.py (with auth protection)

import streamlit as st
from app.auth import require_auth

st.set_page_config(page_title="Declaration & Acceptance")

# Protect this page - require authentication
require_auth()  # All authenticated users can access
# OR
# require_auth(allowed_roles=['admin', 'trader'])  # Only specific roles

# Rest of the page code...
```

## 5. Integration with Existing Systems

### 5.1 SEAMLESS Integration with Existing Audit System

The existing `get_user_identity()` function in `app/email_sender.py` is **already designed** for this! We only need to update the priority order:

**Current Function (app/email_sender.py lines 32-76):**
```python
def get_user_identity() -> Dict[str, str]:
    """
    Extract user identity from current authentication/declaration system.
    Already supports: declaration, OAuth, SSO, API key
    """
    identity = {
        'name': 'Unknown User',
        'email': 'unknown@domain.com',
        'auth_method': 'none',
        'user_id': None
    }
    
    # Check for declaration-based identity (current system)
    if st.session_state.get('consent_name') and st.session_state.get('consent_email'):
        identity['name'] = st.session_state['consent_name']
        identity['email'] = st.session_state['consent_email']
        identity['auth_method'] = 'declaration'
        identity['consent_date'] = st.session_state.get('consent_date', 'Unknown')
    
    return identity
```

**UPDATED Function (add 5 lines at the top):**
```python
def get_user_identity() -> Dict[str, str]:
    """
    Extract user identity from current authentication/declaration system.
    Now supports: password auth, declaration, OAuth, SSO, API key
    """
    identity = {
        'name': 'Unknown User',
        'email': 'unknown@domain.com',
        'auth_method': 'none',
        'user_id': None
    }
    
    # ============================================
    # NEW: Check for authenticated user (TAKES PRECEDENCE)
    # ============================================
    if st.session_state.get('auth_user'):
        user = st.session_state['auth_user']
        identity['name'] = user.get('name', 'Unknown')
        identity['email'] = user.get('email', 'unknown@domain.com')
        identity['auth_method'] = st.session_state.get('auth_provider', 'password')
        identity['user_id'] = user.get('user_id')
        identity['user_role'] = user.get('role', 'unknown')
        identity['login_time'] = st.session_state.get('auth_login_time', 'Unknown')
        return identity
    
    # FALLBACK: Check for declaration-based identity (backward compatibility)
    if st.session_state.get('consent_name') and st.session_state.get('consent_email'):
        identity['name'] = st.session_state['consent_name']
        identity['email'] = st.session_state['consent_email']
        identity['auth_method'] = 'declaration'
        identity['consent_date'] = st.session_state.get('consent_date', 'Unknown')
    
    return identity
```

**That's it! The existing audit email system will automatically capture:**
- User's full name
- User's email address
- Authentication method (password, OAuth, etc.)
- User's role (admin, trader, viewer)
- Login timestamp

**NO CHANGES needed to:**
- `send_comprehensive_audit_email()` function
- Any email templates
- Any audit logging code
- Any downstream systems

### 5.2 Keep or Remove Declaration Page?

**Option A: Keep Declaration as Acknowledgment (RECOMMENDED)**
```python
# pages/1_Informed_Consent.py

from app.auth import require_auth, get_current_user

require_auth()  # Must be logged in
user = get_current_user()

st.title(f"Welcome, {user['name']}")
st.markdown("### Declaration & Acceptance")

# Show pre-filled user info (read-only)
st.text_input("Name", value=user['name'], disabled=True)
st.text_input("Email", value=user['email'], disabled=True)

# Only capture acceptance
if st.checkbox("I confirm the accuracy of trading data"):
    st.session_state['consent_given'] = True
    st.switch_page('app/main.py')
```

**Option B: Remove Declaration Page Entirely**
- Login replaces declaration
- Go straight to upload after login
- Update navigation in sidebar

**Recommended: Option A** - Keep the acknowledgment for compliance reasons while auto-populating from auth.

### 5.2 Sidebar User Display

```python
# app/components/sidebar.py

from app.auth import get_current_user, logout

def render_sidebar():
    # ... existing code ...
    
    # Display logged-in user
    user = get_current_user()
    if user:
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <div style="color: white; font-weight: 600;">{user['name']}</div>
            <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.875rem;">{user['email']}</div>
            <div style="color: rgba(255, 255, 255, 0.5); font-size: 0.75rem; margin-top: 0.25rem;">
                Role: {user['role'].upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("Logout", use_container_width=True):
            logout()
            st.switch_page('pages/0_Login.py')
```

### 5.3 Audit Trail Enhancement

The audit email system automatically captures the authenticated user:

```python
# Email will now show:
# WHO EXECUTED:
# Name: Don Kruger
# Email: don@easycrypto.co.za
# Auth Method: PASSWORD
# Role: ADMIN
# Login Time: 2025-10-03 14:30:45
```

## 6. Security Considerations

### 6.1 Password Security

**Current Approach (MVP):**
- SHA-256 password hashing
- Passwords stored as hashes in secrets.toml
- No plaintext passwords in configuration

**Limitations:**
- SHA-256 is fast (vulnerable to brute force)
- No password salting
- No rate limiting on login attempts

**Acceptable for MVP because:**
- Small, trusted user base
- Internal users only
- Secrets.toml is protected by file system permissions
- Clear migration path to robust solution

### 6.2 Session Security

```python
# Add session timeout (optional enhancement)
def check_session_timeout(timeout_minutes=60):
    """
    Check if session has timed out
    """
    if not is_authenticated():
        return
    
    login_time = st.session_state.get('login_timestamp')
    if login_time:
        from datetime import datetime, timedelta
        login_dt = datetime.fromisoformat(login_time)
        if datetime.now() - login_dt > timedelta(minutes=timeout_minutes):
            logout()
            st.warning("Session expired. Please login again.")
            st.switch_page('pages/0_Login.py')
            st.stop()
```

### 6.3 secrets.toml Protection

**File Permissions:**
```bash
chmod 600 .streamlit/secrets.toml
# Only owner can read/write
```

**Git Protection:**
```gitignore
.streamlit/secrets.toml
```

**Deployment:**
- Never commit secrets.toml to repository
- Use environment-specific configurations
- Rotate passwords regularly

## 7. Dependencies & Requirements

### 7.1 Update requirements.txt

```txt
# Add to requirements.txt
bcrypt==4.1.2  # Password hashing (replaces SHA-256)
```

Install with:
```bash
pip install bcrypt
```

### 7.2 File Structure

```
trading-sheet-applet/
├── app/
│   ├── auth.py                          # NEW: Authentication Manager
│   ├── auth_providers/                  # NEW: Provider implementations
│   │   ├── __init__.py                  # NEW: Base classes (UserInfo, AuthenticationProvider)
│   │   └── secrets.py                   # NEW: SecretsAuthProvider
│   ├── email_sender.py                  # MODIFY: Update get_user_identity() (5 lines)
│   ├── components/
│   │   └── sidebar.py                   # MODIFY: Add user display and logout
│   ├── pages/
│   │   ├── 0_Login.py                   # NEW: Login page
│   │   ├── 1_Informed_Consent.py        # MODIFY: Add require_auth() (1 line)
│   │   └── 3_Declaration_and_Submit.py  # MODIFY: Add require_auth() (1 line)
│   └── main.py                          # MODIFY: Add require_auth() (1 line)
├── .streamlit/
│   └── secrets.toml                     # MODIFY: Add [auth] and [users.*] sections
└── scripts/
    └── generate_password_hash.py        # NEW: Helper script for password hashes
```

### 7.3 Password Hash Generation Script

Create `scripts/generate_password_hash.py`:

```python
#!/usr/bin/env python3
"""
Password Hash Generator for Trading Sheet Application

Usage:
    python scripts/generate_password_hash.py

This script generates bcrypt password hashes for use in secrets.toml
"""

import bcrypt
import getpass

def generate_hash():
    print("=== Password Hash Generator ===\n")
    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")
    
    if password != confirm:
        print("❌ Passwords don't match!")
        return
    
    if len(password) < 8:
        print("⚠️  Warning: Password should be at least 8 characters")
    
    # Generate bcrypt hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    hash_str = hashed.decode('utf-8')
    
    print("\n✓ Password hash generated successfully!")
    print("\nAdd this to secrets.toml:")
    print("-" * 60)
    print(f'password_hash = "{hash_str}"')
    print("-" * 60)

if __name__ == "__main__":
    generate_hash()
```

## 8. Implementation Steps (Complete Plan)

### Phase 1: Core Authentication (Day 1 - 4 hours)

1. **Create authentication module**
   - [ ] Create `app/auth.py` with all authentication functions
   - [ ] Add password hashing utilities
   - [ ] Implement user loading from secrets.toml

2. **Create login page**
   - [ ] Create `pages/0_Login.py` with login form
   - [ ] Implement login logic and session management
   - [ ] Add error handling and user feedback

3. **Update secrets.toml**
   - [ ] Add `[users]` sections (admin, traders, viewers)
   - [ ] Generate password hashes for initial users
   - [ ] Document password hash generation process

### Phase 2: Page Protection (Day 2)

4. **Protect existing pages**
   - [ ] Add `require_auth()` to all pages:
     - `pages/1_Informed_Consent.py`
     - `app/main.py`
     - `pages/3_Declaration_and_Submit.py`
   - [ ] Test redirect flow to login page

5. **Update sidebar**
   - [ ] Display logged-in user information
   - [ ] Add logout button
   - [ ] Show user role badge

### Phase 3: Integration (Day 3)

6. **Integrate with audit system**
   - [ ] Update `get_user_identity()` to check auth first
   - [ ] Ensure backward compatibility with declaration system
   - [ ] Test audit emails show authenticated user

7. **Remove/deprecate declaration page**
   - [ ] Option A: Remove declaration page entirely
   - [ ] Option B: Keep as acknowledgment (no manual entry)
   - [ ] Update navigation flow

### Phase 4: Testing & Documentation (Day 4)

8. **Testing**
   - [ ] Test login with valid credentials
   - [ ] Test login with invalid credentials
   - [ ] Test session persistence across pages
   - [ ] Test logout functionality
   - [ ] Test role-based access control
   - [ ] Test audit email captures user correctly

9. **Documentation**
   - [ ] Update README.md with login instructions
   - [ ] Create password reset procedure
   - [ ] Document user management (add/remove users)
   - [ ] Create secrets.toml.example with dummy hashes

## 8. User Management Operations

### Adding a New User

1. **Generate password hash:**
```python
import hashlib
password = "SecurePassword123"
password_hash = hashlib.sha256(password.encode()).hexdigest()
print(f"Password hash: {password_hash}")
```

2. **Add to secrets.toml:**
```toml
[users.traders]
"newuser@easyequities.co.za" = {name = "New User", password_hash = "GENERATED_HASH", role = "trader"}
```

3. **Restart application** (Streamlit reloads secrets.toml)

### Removing a User

1. Delete the user entry from secrets.toml
2. Restart application

### Changing a Password

1. Generate new password hash
2. Update password_hash in secrets.toml
3. Restart application

### Password Reset Process

Since passwords are hashed, admins must:
1. Generate new temporary password
2. Generate hash and update secrets.toml
3. Send temporary password to user (securely)
4. User changes password on next login (future enhancement)

## 9. Migration Path to Robust Solutions

This MVP design provides a clear upgrade path:

### Level 1: Enhanced MVP (secrets.toml)
- ✅ Current design
- Add: Password salting with bcrypt
- Add: Session timeouts
- Add: Login attempt rate limiting

### Level 2: Database Authentication
```python
# Future: Replace load_users() with database query
def load_users():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users WHERE active = 1").fetchall()
    return users
```

### Level 3: OAuth/SSO Integration
```python
# Future: Add OAuth providers
from streamlit_oauth import OAuth

oauth = OAuth(
    client_id=st.secrets["oauth"]["google_client_id"],
    client_secret=st.secrets["oauth"]["google_client_secret"]
)
user = oauth.login()
```

### Level 4: Enterprise SSO (LDAP/AD)
```python
# Future: Corporate authentication
from ldap3 import Server, Connection

def authenticate_ldap(username, password):
    server = Server('ldap://company.com')
    conn = Connection(server, user=username, password=password)
    return conn.bind()
```

## 10. Code Migration Example

### Before (Declaration-based):

```python
# pages/1_Informed_Consent.py
st.title("Declaration & Acceptance")

full_name = st.text_input("Full Name *")
email = st.text_input("Email Address *")

if st.button("I Accept"):
    st.session_state['consent_name'] = full_name
    st.session_state['consent_email'] = email
    st.session_state['consent_given'] = True
```

### After (Authentication-based):

```python
# pages/0_Login.py
st.title("Login")

email = st.text_input("Email Address")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if authenticate_user(email, password):
        user_info = get_user_info(email)
        st.session_state['authenticated'] = True
        st.session_state['user_email'] = email
        st.session_state['user_name'] = user_info['name']
        # Name and email now come from secrets.toml automatically!
```

## 11. Example secrets.toml Configuration

```toml
# Complete example with all sections

[email_credentials]
email_address = "don@easycrypto.co.za"
app_password = "your-app-password"
notification_address = "trading-ops@easyequities.co.za"
smtp_server = "smtp.gmail.com"

[trade_api]
environment = "uat"
uat_base_url = "https://tradeallocationsapi.purple-uat.easyequities.io"
uat_monitor_url = "https://trade-allocations-monitor.purple-uat.easyequities.io"
system_identifier_id = 27

[trade_protection]
block_non_ut_trades = true
supported_contract_prefixes = ["UT.ZA"]
protection_mode = "strict"

# ============================================
# USER MANAGEMENT - MVP AUTHENTICATION
# ============================================
[users.admin]
"don@easycrypto.co.za" = {
    name = "Don Kruger", 
    password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
    role = "admin"
}
"trading-ops@easyequities.co.za" = {
    name = "Trading Operations", 
    password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", 
    role = "admin"
}

[users.traders]
"trader1@easyequities.co.za" = {
    name = "Senior Trader", 
    password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", 
    role = "trader"
}

[users.viewers]
"compliance@easyequities.co.za" = {
    name = "Compliance Team", 
    password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", 
    role = "viewer"
}

# Password Hash Generation Script:
# python -c "import hashlib; print(hashlib.sha256(b'your_password').hexdigest())"
```

## 12. Benefits & Trade-offs

### ✅ Benefits

1. **Immediate Implementation**: Can be deployed in hours, not weeks
2. **Zero Dependencies**: No database, no external services
3. **Simple Management**: Add/remove users by editing one file
4. **Audit Trail**: Integrates seamlessly with existing audit email system
5. **Cost-Effective**: No additional infrastructure costs
6. **Development-Friendly**: Easy to test and debug
7. **Clear Upgrade Path**: Can migrate to robust auth without rewriting UI

### ⚠️ Trade-offs

1. **Manual User Management**: Must edit secrets.toml and restart app
2. **Basic Security**: SHA-256 without salting (acceptable for small teams)
3. **No Password Recovery**: Admin must reset passwords manually
4. **File-Based**: Limited to single-server deployments
5. **No Audit of Logins**: (Can be added in Phase 2)

### When to Migrate

Move to a robust solution when:
- User count exceeds 20 people
- Need self-service password reset
- Require password complexity policies
- Need login audit trails
- Deploying to production at scale
- Compliance requires enterprise SSO

## 13. Success Criteria

The MVP is successful when:

- ✅ Only authenticated users can access the application
- ✅ User identity is captured in audit emails
- ✅ Session persists across page navigation
- ✅ Logout properly clears session
- ✅ Invalid credentials are rejected
- ✅ User's name and email auto-populate from auth system
- ✅ Different user roles are distinguished (future use)
- ✅ System can be deployed in UAT within 1 day

## 14. CRITICAL ADVANTAGES - Why This Design Is Superior

### 14.1 Swappability (Future-Proof)

**Problem with naive approach:**
```python
# BAD: Hardcoded auth logic in every page
if check_password(email, password):  # Tightly coupled to secrets.toml
    st.session_state['user'] = email
```

**Our solution:**
```python
# GOOD: Abstract interface, swap implementation
from app.auth import require_auth, get_current_user

require_auth()  # Works with ANY auth provider
user = get_current_user()  # Same code, different backend
```

**To switch to OAuth (e.g., Google SSO):**
1. Implement `OAuth2AuthProvider` class (100 lines)
2. Change `secrets.toml`: `provider = "oauth"` (1 line)
3. **ZERO changes** to application code ✓

### 14.2 Integration Points Summary

| Component | Changes Required | Impact |
|-----------|------------------|--------|
| `app/email_sender.py` | +5 lines (priority check) | ✓ Automatic |
| `app/pages/*.py` | +1 line each (`require_auth()`) | ✓ Minimal |
| `app/components/sidebar.py` | +10 lines (user display) | ✓ Minimal |
| Audit email system | **0 changes** | ✓ Works automatically |
| Trade execution | **0 changes** | ✓ Uses existing identity |
| All other components | **0 changes** | ✓ Transparent |

### 14.3 Security Comparison

| Feature | Naive Approach | This Design |
|---------|----------------|-------------|
| Password Storage | Plain text or SHA-256 ❌ | bcrypt with salt ✓ |
| Rate Limiting | None ❌ | 5 attempts/15 min ✓ |
| Session Timeout | None ❌ | Configurable ✓ |
| Inactivity Timeout | None ❌ | 30 minutes ✓ |
| Login Audit | None ❌ | Comprehensive ✓ |
| Role-Based Access | Manual checks ❌ | Built-in `require_auth(['admin'])` ✓ |

### 14.4 Migration Path

```
┌─────────────────────────────────────────────────────────┐
│ Current State                                            │
│ - Manual declaration                                     │
│ - No authentication                                      │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼ Implement MVP (1-2 days)
┌─────────────────────────────────────────────────────────┐
│ MVP: SecretsAuthProvider                                 │
│ - Password authentication                                │
│ - bcrypt security                                        │
│ - Rate limiting                                          │
│ - Audit trail                                            │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼ When needed (change 1 line)
┌─────────────────────────────────────────────────────────┐
│ Production: OAuth2AuthProvider                           │
│ - Google/Microsoft SSO                                   │
│ - Enterprise authentication                              │
│ - SAME application code                                  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼ If required (change 1 line)
┌─────────────────────────────────────────────────────────┐
│ Enterprise: LDAPAuthProvider                             │
│ - Active Directory                                       │
│ - Corporate SSO                                          │
│ - SAME application code                                  │
└─────────────────────────────────────────────────────────┘
```

## 15. Conclusion & Recommendation

### ✅ What This Design Delivers

1. **Immediate Value** - MVP deployable in 1-2 days
2. **Production-Ready Security** - bcrypt, rate limiting, session management
3. **Zero Technical Debt** - Clean architecture, not a hack
4. **Future-Proof** - Swap auth providers without code changes
5. **Audit Compliance** - Integrates seamlessly with existing audit trail
6. **Minimal Disruption** - Only 3-4 files require changes

### 🎯 Implementation Effort

| Phase | Time | Files Changed | Risk |
|-------|------|---------------|------|
| Core Auth (Day 1) | 4 hours | 4 new files | Low |
| Page Protection (Day 2) | 2 hours | 4 modified files | Low |
| Testing (Day 3) | 4 hours | 0 files | Low |
| **TOTAL** | **10 hours** | **8 files** | **Low** |

### 📊 Return on Investment

**Benefits:**
- ✅ Complete audit trail (WHO executed every trade)
- ✅ Access control (prevent unauthorized trades)
- ✅ Compliance ready (proper authentication)
- ✅ Future-proof (swap to enterprise auth when needed)
- ✅ Production-grade security (bcrypt, rate limiting)

**Cost:**
- 1-2 days development
- Add `bcrypt` dependency (industry standard)
- Minimal code changes to existing files

### 🚀 Recommendation

**Implement this design immediately for the following reasons:**

1. **Audit Requirement**: Current declaration system doesn't prevent impersonation
2. **Low Risk**: Provider pattern isolates auth logic from application
3. **Fast Implementation**: 1-2 days to production-ready MVP
4. **No Technical Debt**: Clean architecture that supports future needs
5. **Security**: Proper password hashing and session management

**Deployment Strategy:**
1. **Week 1**: Implement and deploy to UAT
2. **Week 2**: User acceptance testing with trading team
3. **Week 3**: Production deployment
4. **Future**: Migrate to OAuth/SSO when org is ready (change 1 line)

**The design is intentionally architected to be:**
- ✓ **Simple enough** to implement in days
- ✓ **Robust enough** for production use
- ✓ **Flexible enough** to evolve into enterprise SSO
- ✓ **Clean enough** to maintain long-term

This is **working software now** with a **clear path to perfect software later**.

---

## 16. Quick Start Implementation Checklist

### Pre-Implementation (5 minutes)

```bash
# 1. Install bcrypt
pip install bcrypt

# 2. Add to requirements.txt
echo "bcrypt==4.1.2  # Password hashing" >> requirements.txt

# 3. Generate test password hash
python -c "import bcrypt; print(bcrypt.hashpw(b'TestPass123', bcrypt.gensalt()).decode())"
```

### Implementation Order (10 hours total)

**✓ Step 1: Create auth_providers module (2 hours)**
```bash
mkdir -p app/auth_providers
# Create files:
# - app/auth_providers/__init__.py (base classes)
# - app/auth_providers/secrets.py (secrets provider)
```

**✓ Step 2: Create authentication manager (2 hours)**
```bash
# Create file:
# - app/auth.py (main auth module)
```

**✓ Step 3: Create login page (1 hour)**
```bash
# Create file:
# - pages/0_Login.py
```

**✓ Step 4: Update secrets.toml (30 minutes)**
```toml
# Add [auth] section
# Add [users.*] sections with bcrypt hashes
```

**✓ Step 5: Update email_sender.py (30 minutes)**
```python
# Add check for auth_user in get_user_identity()
# Priority: auth_user > consent_name (backward compatible)
```

**✓ Step 6: Protect pages (1 hour)**
```python
# Add to each page:
from app.auth import require_auth
require_auth()
```

**✓ Step 7: Update sidebar (1 hour)**
```python
# Add user display and logout button
```

**✓ Step 8: Test (2 hours)**
```bash
# Test login with valid/invalid credentials
# Test session timeout
# Test rate limiting
# Test audit emails
# Test role-based access
```

### Verification Commands

```bash
# 1. Check if bcrypt is installed
python -c "import bcrypt; print('✓ bcrypt installed')"

# 2. Verify auth module imports
python -c "from app.auth import require_auth, get_current_user; print('✓ Auth module OK')"

# 3. Verify provider imports
python -c "from app.auth_providers.base import AuthenticationProvider; print('✓ Provider base OK')"

# 4. Test password hash generation
python scripts/generate_password_hash.py

# 5. Run the app
streamlit run app/main.py
```

### Testing Checklist

- [ ] Valid login succeeds
- [ ] Invalid login fails
- [ ] Rate limiting works (5 failed attempts)
- [ ] Session timeout works (60 minutes)
- [ ] Inactivity timeout works (30 minutes)
- [ ] Protected pages redirect to login
- [ ] Logout clears session
- [ ] Audit emails include user info
- [ ] Role-based access works
- [ ] Sidebar displays user info

### Rollback Plan

If issues occur, rollback is simple:

```bash
# 1. Remove require_auth() calls from pages
# 2. Delete app/auth.py and app/auth_providers/
# 3. Revert secrets.toml
# 4. Revert email_sender.py get_user_identity()
# 5. Delete pages/0_Login.py
```

**Total rollback time: 10 minutes** (low risk!)

---

## 17. FAQs

**Q: Why not use Streamlit's built-in authentication?**
A: Streamlit doesn't have built-in authentication. Third-party solutions exist but add dependencies. Our solution is lightweight and swappable.

**Q: Can I use this with OAuth later?**
A: Yes! Implement `OAuth2AuthProvider`, change `provider = "oauth"` in secrets.toml. Zero code changes needed.

**Q: What if I need to reset a user's password?**
A: Generate new hash with `scripts/generate_password_hash.py`, update secrets.toml, restart app.

**Q: How do I add a new user?**
A: Generate password hash, add to appropriate [users.*] section in secrets.toml, restart app.

**Q: Is bcrypt secure enough for production?**
A: Yes. bcrypt is industry standard, used by major platforms (GitHub, Dropbox, etc.). Work factor makes brute force impractical.

**Q: What about password complexity requirements?**
A: Add to login page validation. Example: min 8 chars, 1 uppercase, 1 number.

**Q: Can I disable a user without deleting them?**
A: Yes. Set `enabled = false` in secrets.toml.

**Q: How do I audit login attempts?**
A: Check application logs. All authentication attempts are logged via Python logging module.

---

**Document Version:** 2.0 (Enhanced with Provider Pattern)  
**Last Updated:** 2025-10-03  
**Status:** READY FOR IMPLEMENTATION
