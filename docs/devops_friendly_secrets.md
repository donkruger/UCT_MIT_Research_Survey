# DevOps-Friendly Secrets Implementation Guide
## Trading Sheet Applet - Solution Design

---

## Executive Summary

This document describes how to migrate the **Trading Sheet Applet** from committed `secrets.toml` files to a **DevOps-friendly secrets management** approach compatible with **HashiCorp Vault** and **AWS ECS Fargate** deployments.

**Goal**: Keep application code unchanged (continues using `st.secrets`) while enabling secrets to be injected via environment variables at container startup—eliminating hardcoded secrets from the repository.

---

## Current State Analysis

### Existing Secrets Structure

The application currently uses `.streamlit/secrets.toml` with the following sections:

```toml
[email_credentials]      # SMTP credentials for audit emails
[llm_api]               # Gemini API key for AI features
[trade_api]             # Trade Allocations API configuration
[trade_protection]      # Security settings for UT-only enforcement
[auth]                  # Authentication configuration
[users.admin]           # User credentials (bcrypt hashes)
```

### Critical Requirements

1. **Zero application code changes** - All Python code continues using `st.secrets[...]`
2. **Preserve authentication** - User management and bcrypt hashes must work identically
3. **Maintain security features** - UT-only protection, rate limiting, audit trail
4. **Support multiple environments** - UAT, QA, Production with different configurations
5. **ECS Fargate compatibility** - Environment variables from HashiCorp Vault via Task Definitions

---

## Solution Architecture

### High-Level Approach

We'll implement a **template-based rendering system** that generates `.streamlit/secrets.toml` from environment variables at container startup:

1. **Template File**: `.streamlit/secrets.template.toml` with `${VAR:-default}` placeholders (committed to repo)
2. **Entrypoint Script**: `entrypoint.sh` renders the template before Streamlit starts (committed to repo)
3. **Environment Variables**: Injected by ECS Task Definitions from HashiCorp Vault (not in repo)
4. **Runtime Secrets**: `.streamlit/secrets.toml` generated in container (never committed)

### Benefits

✅ **No code changes required** - Application continues reading `st.secrets`  
✅ **HashiCorp Vault integration** - Secrets injected via ECS environment variables  
✅ **Fail-fast validation** - Container exits if required secrets are missing  
✅ **Environment flexibility** - Same image works across UAT/QA/Prod with different configs  
✅ **Audit compliance** - Complete traceability of secrets usage  
✅ **Local development** - Developers use `.env` files (not committed)  

---

## Implementation Plan

### Phase 1: Repository Changes

#### 1.1 Create Template File

**New File**: `.streamlit/secrets.template.toml`

```toml
# =============================================================================
# TRADING SHEET APPLET - SECRETS TEMPLATE
# =============================================================================
# This file is committed to the repository with placeholders.
# At runtime, entrypoint.sh replaces ${VAR:-default} with environment variables.
# =============================================================================

# -----------------------------------------------------------------------------
# EMAIL CONFIGURATION - Audit Trail & Notifications
# -----------------------------------------------------------------------------
[email_credentials]
email_address = "${EMAIL_ADDRESS:-trading@easyequities.co.za}"
app_password = "${EMAIL_APP_PASSWORD:-}"
notification_address = "${EMAIL_NOTIFICATION_ADDRESS:-trading-ops@easyequities.co.za}"
smtp_server = "${EMAIL_SMTP_SERVER:-smtp.gmail.com}"

# -----------------------------------------------------------------------------
# LLM API - AI Features (Optional)
# -----------------------------------------------------------------------------
[llm_api]
gemini_key = "${LLM_GEMINI_API_KEY:-}"

# -----------------------------------------------------------------------------
# TRADE ALLOCATIONS API - Core Trading Functionality
# -----------------------------------------------------------------------------
[trade_api]
# Environment selection: "uat", "qa", or "prod"
environment = "${TRADE_API_ENVIRONMENT:-uat}"

# UAT Environment URLs
uat_base_url = "${TRADE_API_UAT_BASE_URL:-https://tradeallocationsapi.purple-uat.easyequities.io}"
uat_monitor_url = "${TRADE_API_UAT_MONITOR_URL:-https://trade-allocations-monitor.purple-uat.easyequities.io}"

# QA Environment URLs
qa_base_url = "${TRADE_API_QA_BASE_URL:-https://tradeallocationsapi.purple-qa.easyequities.io}"
qa_monitor_url = "${TRADE_API_QA_MONITOR_URL:-https://trade-allocations-monitor.purple-qa.easyequities.io}"

# Production Environment URLs
prod_base_url = "${TRADE_API_PROD_BASE_URL:-https://tradeallocationsapi.easyequities.io}"
prod_monitor_url = "${TRADE_API_PROD_MONITOR_URL:-https://trade-allocations-monitor.easyequities.io}"

# System Configuration
system_identifier_id = ${TRADE_API_SYSTEM_ID:-27}
api_timeout = ${TRADE_API_TIMEOUT:-30}
max_retry_attempts = ${TRADE_API_MAX_RETRIES:-3}
status_polling_interval = ${TRADE_API_POLLING_INTERVAL:-5}
max_polling_duration = ${TRADE_API_MAX_POLLING_DURATION:-300}

# Authentication (Bearer token for API)
api_key = "${TRADE_API_KEY:-}"

# Optional: Trader configuration
default_trader_id = ${TRADE_API_DEFAULT_TRADER_ID:-45314}

# -----------------------------------------------------------------------------
# TRADE PROTECTION - UT-Only Security Enforcement
# -----------------------------------------------------------------------------
[trade_protection]
# SECURITY: Fail-safe default - protection always enabled unless explicitly disabled
block_non_ut_trades = ${TRADE_PROTECTION_BLOCK_NON_UT:-true}
supported_contract_prefixes = "${TRADE_PROTECTION_PREFIXES:-UT.ZA}"
protection_mode = "${TRADE_PROTECTION_MODE:-strict}"
audit_all_validations = ${TRADE_PROTECTION_AUDIT_ALL:-true}

# SECURITY: Environment-specific overrides (UAT/QA only)
allow_protection_override = ${TRADE_PROTECTION_ALLOW_OVERRIDE:-false}
max_validation_attempts = ${TRADE_PROTECTION_MAX_ATTEMPTS:-3}

# -----------------------------------------------------------------------------
# AUTHENTICATION CONFIGURATION
# -----------------------------------------------------------------------------
[auth]
# Authentication provider selection (swap without code changes)
provider = "${AUTH_PROVIDER:-secrets}"

# Session configuration
session_timeout_minutes = ${AUTH_SESSION_TIMEOUT:-60}
session_inactivity_timeout_minutes = ${AUTH_INACTIVITY_TIMEOUT:-30}

# Rate limiting (brute force protection)
max_login_attempts = ${AUTH_MAX_LOGIN_ATTEMPTS:-5}
lockout_duration_minutes = ${AUTH_LOCKOUT_DURATION:-15}

# Audit configuration
log_login_attempts = ${AUTH_LOG_ATTEMPTS:-true}
log_failed_attempts_only = ${AUTH_LOG_FAILED_ONLY:-false}

# -----------------------------------------------------------------------------
# USER MANAGEMENT (MVP - secrets provider)
# -----------------------------------------------------------------------------
# CRITICAL: Use bcrypt hashes, NOT plain text
# Note: User hashes are loaded from separate environment variables
# Pattern: USERS_ADMIN_<EMAIL_SAFE> = "name|hash|role|enabled"
# Example: USERS_ADMIN_DON_EASYEQUITIES = "Don Kruger|$2b$12$...|admin|true"
# -----------------------------------------------------------------------------
[users.admin]
# Users will be constructed by entrypoint.sh from USERS_ADMIN_* environment variables
# This section is populated dynamically at runtime
```

**Key Design Decisions**:
- **Boolean values**: Unquoted (`true`/`false`) for TOML type correctness
- **Array values**: Strings like `"UT.ZA"` (application can split if needed)
- **User hashes**: Special handling in entrypoint.sh to construct `[users.admin]` section
- **Defaults**: Safe for local development, overridden in production

#### 1.2 Create Entrypoint Script

**New File**: `entrypoint.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# TRADING SHEET APPLET - ENTRYPOINT SCRIPT
# =============================================================================
# Renders .streamlit/secrets.toml from template using environment variables
# Validates required secrets and fails fast if missing
# =============================================================================

# Required for non-dev deployments (set to "true" in ECS)
: "${STRICT_STARTUP:=false}"

echo "🔧 Trading Sheet Applet - Starting configuration..."

# -----------------------------------------------------------------------------
# Validation Helper Functions
# -----------------------------------------------------------------------------
require() {
  local var="$1"
  if [ "${STRICT_STARTUP}" = "true" ]; then
    if [ -z "${!var:-}" ]; then
      echo "❌ FATAL: Required environment variable '$var' is not set." >&2
      exit 1
    fi
  else
    if [ -z "${!var:-}" ]; then
      echo "⚠️  WARNING: Optional environment variable '$var' is not set (non-strict mode)." >&2
    fi
  fi
}

# -----------------------------------------------------------------------------
# Critical Secrets Validation
# -----------------------------------------------------------------------------
echo "🔍 Validating critical environment variables..."

# Email credentials (required for audit trail)
require EMAIL_ADDRESS
require EMAIL_APP_PASSWORD
require EMAIL_NOTIFICATION_ADDRESS

# Trade API credentials (required for core functionality)
require TRADE_API_ENVIRONMENT
require TRADE_API_KEY

# Authentication configuration
require AUTH_PROVIDER

# At least one admin user (for MVP authentication)
if [ "${STRICT_STARTUP}" = "true" ]; then
  if ! env | grep -q '^USERS_ADMIN_'; then
    echo "❌ FATAL: No admin users configured (no USERS_ADMIN_* variables found)." >&2
    exit 1
  fi
fi

echo "✅ Critical validations passed"

# -----------------------------------------------------------------------------
# Create .streamlit directory
# -----------------------------------------------------------------------------
mkdir -p .streamlit

# -----------------------------------------------------------------------------
# Check if we should regenerate secrets
# -----------------------------------------------------------------------------
if [ -f .streamlit/secrets.toml ] && [ "${OVERWRITE_SECRETS:-false}" != "true" ]; then
  echo "ℹ️  Using existing .streamlit/secrets.toml (set OVERWRITE_SECRETS=true to regenerate)"
  exec "$@"
fi

echo "🔨 Rendering secrets.toml from template..."

# -----------------------------------------------------------------------------
# Render Base Template (all standard sections)
# -----------------------------------------------------------------------------
if command -v envsubst >/dev/null 2>&1; then
  envsubst < .streamlit/secrets.template.toml > .streamlit/secrets.toml.tmp
else
  # POSIX-compatible fallback using AWK
  awk '{
    line=$0
    while (match(line, /\$\{[A-Za-z_][A-Za-z0-9_]*(:-[^}]*)?\}/)) {
      tok=substr(line, RSTART+2, RLENGTH-3)
      split(tok, a, ":-")
      var=a[1]
      def=(length(a)>1)?a[2]:""
      val=(var in ENVIRON && ENVIRON[var]!="")?ENVIRON[var]:def
      gsub("\\${"var"(:-[^}]*)?}", val, line)
    }
    print line
  }' .streamlit/secrets.template.toml > .streamlit/secrets.toml.tmp
fi

# -----------------------------------------------------------------------------
# Construct [users.admin] Section from Environment Variables
# -----------------------------------------------------------------------------
# Expected format: USERS_ADMIN_<IDENTIFIER> = "email|name|password_hash|role|enabled"
# Example: USERS_ADMIN_DON_EE = "don@easyequities.co.za|Don Kruger|$2b$12$...|admin|true"
# -----------------------------------------------------------------------------
echo "" >> .streamlit/secrets.toml.tmp
echo "# User accounts (generated from USERS_ADMIN_* environment variables)" >> .streamlit/secrets.toml.tmp

user_count=0
for var in $(env | grep '^USERS_ADMIN_' | cut -d= -f1 | sort); do
  user_data="${!var}"
  
  # Parse user data: email|name|password_hash|role|enabled
  IFS='|' read -r email name password_hash role enabled <<< "$user_data"
  
  if [ -n "$email" ] && [ -n "$password_hash" ]; then
    # Construct TOML user entry
    # Format: "email" = {name = "...", password_hash = "...", role = "...", enabled = true}
    echo "\"${email}\" = {name = \"${name}\", password_hash = \"${password_hash}\", role = \"${role}\", enabled = ${enabled}}" >> .streamlit/secrets.toml.tmp
    user_count=$((user_count + 1))
  else
    echo "⚠️  WARNING: Invalid user data format for $var (skipping)" >&2
  fi
done

if [ "$user_count" -eq 0 ]; then
  echo "⚠️  WARNING: No valid admin users configured" >&2
  if [ "${STRICT_STARTUP}" = "true" ]; then
    echo "❌ FATAL: At least one admin user required in strict mode" >&2
    exit 1
  fi
fi

echo "✅ Configured $user_count admin user(s)"

# Move temp file to final location
mv .streamlit/secrets.toml.tmp .streamlit/secrets.toml

# -----------------------------------------------------------------------------
# Optional: Render config.toml for UI customization
# -----------------------------------------------------------------------------
if [ -f .streamlit/config.template.toml ]; then
  echo "🎨 Rendering config.toml from template..."
  if command -v envsubst >/dev/null 2>&1; then
    envsubst < .streamlit/config.template.toml > .streamlit/config.toml
  else
    awk '{
      line=$0
      while (match(line, /\$\{[A-Za-z_][A-Za-z0-9_]*(:-[^}]*)?\}/)) {
        tok=substr(line, RSTART+2, RLENGTH-3)
        split(tok, a, ":-")
        var=a[1]
        def=(length(a)>1)?a[2]:""
        val=(var in ENVIRON && ENVIRON[var]!="")?ENVIRON[var]:def
        gsub("\\${"var"(:-[^}]*)?}", val, line)
      }
      print line
    }' .streamlit/config.template.toml > .streamlit/config.toml
  fi
fi

# -----------------------------------------------------------------------------
# Final Sanity Checks
# -----------------------------------------------------------------------------
if [ ! -f .streamlit/secrets.toml ]; then
  echo "❌ FATAL: Failed to generate .streamlit/secrets.toml" >&2
  exit 1
fi

echo "✅ Secrets configuration complete"
echo "🚀 Starting application..."

# -----------------------------------------------------------------------------
# Hand off to the actual application command
# -----------------------------------------------------------------------------
exec "$@"
```

**Key Features**:
- **Fail-fast validation**: Exits immediately if critical secrets missing (when `STRICT_STARTUP=true`)
- **User hash parsing**: Constructs `[users.admin]` from `USERS_ADMIN_*` environment variables
- **Local development friendly**: Uses existing secrets.toml unless `OVERWRITE_SECRETS=true`
- **Portable**: Works with or without `envsubst` (AWK fallback)

#### 1.3 Create Local Development Example

**New File**: `.env.example`

```bash
# =============================================================================
# TRADING SHEET APPLET - LOCAL DEVELOPMENT ENVIRONMENT EXAMPLE
# =============================================================================
# Copy this file to .env and fill in your actual values
# NEVER commit .env to the repository
# =============================================================================

# -----------------------------------------------------------------------------
# Startup Configuration
# -----------------------------------------------------------------------------
STRICT_STARTUP=false              # Set to "true" to enforce all validations
OVERWRITE_SECRETS=false           # Set to "true" to regenerate secrets.toml

# -----------------------------------------------------------------------------
# Email Configuration (Required for audit trail)
# -----------------------------------------------------------------------------
EMAIL_ADDRESS=trading@easyequities.co.za
EMAIL_APP_PASSWORD=your-gmail-app-password-here
EMAIL_NOTIFICATION_ADDRESS=trading-ops@easyequities.co.za
EMAIL_SMTP_SERVER=smtp.gmail.com

# -----------------------------------------------------------------------------
# LLM API (Optional - for AI features)
# -----------------------------------------------------------------------------
LLM_GEMINI_API_KEY=your-gemini-api-key-here

# -----------------------------------------------------------------------------
# Trade Allocations API (Required for core functionality)
# -----------------------------------------------------------------------------
TRADE_API_ENVIRONMENT=uat         # Options: uat, qa, prod
TRADE_API_KEY=your-bearer-token-here

# UAT URLs (default)
TRADE_API_UAT_BASE_URL=https://tradeallocationsapi.purple-uat.easyequities.io
TRADE_API_UAT_MONITOR_URL=https://trade-allocations-monitor.purple-uat.easyequities.io

# QA URLs
TRADE_API_QA_BASE_URL=https://tradeallocationsapi.purple-qa.easyequities.io
TRADE_API_QA_MONITOR_URL=https://trade-allocations-monitor.purple-qa.easyequities.io

# Production URLs
TRADE_API_PROD_BASE_URL=https://tradeallocationsapi.easyequities.io
TRADE_API_PROD_MONITOR_URL=https://trade-allocations-monitor.easyequities.io

# System configuration
TRADE_API_SYSTEM_ID=27
TRADE_API_TIMEOUT=30
TRADE_API_MAX_RETRIES=3
TRADE_API_POLLING_INTERVAL=5
TRADE_API_MAX_POLLING_DURATION=300
TRADE_API_DEFAULT_TRADER_ID=45314

# -----------------------------------------------------------------------------
# Trade Protection (Security settings)
# -----------------------------------------------------------------------------
TRADE_PROTECTION_BLOCK_NON_UT=true
TRADE_PROTECTION_PREFIXES=UT.ZA
TRADE_PROTECTION_MODE=strict      # Options: strict, audit_warn
TRADE_PROTECTION_AUDIT_ALL=true
TRADE_PROTECTION_ALLOW_OVERRIDE=false
TRADE_PROTECTION_MAX_ATTEMPTS=3

# -----------------------------------------------------------------------------
# Authentication Configuration
# -----------------------------------------------------------------------------
AUTH_PROVIDER=secrets              # Options: secrets, oauth, ldap, database
AUTH_SESSION_TIMEOUT=60
AUTH_INACTIVITY_TIMEOUT=30
AUTH_MAX_LOGIN_ATTEMPTS=5
AUTH_LOCKOUT_DURATION=15
AUTH_LOG_ATTEMPTS=true
AUTH_LOG_FAILED_ONLY=false

# -----------------------------------------------------------------------------
# Admin Users (MVP - bcrypt hashed passwords)
# -----------------------------------------------------------------------------
# Format: USERS_ADMIN_<IDENTIFIER> = "email|name|password_hash|role|enabled"
# Generate hash: python3 -c "import bcrypt; print(bcrypt.hashpw(b'YourPassword', bcrypt.gensalt()).decode())"
# -----------------------------------------------------------------------------
USERS_ADMIN_DON_EE="don@easyequities.co.za|Don Kruger (EasyEquities)|\$2b\$12\$reMoGR/59jGtr/KIirPNE.exovMzGd4vZsDaoJf/JopaUe3jAXz.W|admin|true"
USERS_ADMIN_DON_EC="don@easycrypto.co.za|Don Kruger (EasyCrypto)|\$2b\$12\$bBBt5fsYb0M0awoswlnxbOrHmTTgpTQEoNq1I/mXPEDVok9TX9I72|admin|true"
```

#### 1.4 Update .gitignore

Add to `.gitignore`:

```
# Secrets (never commit)
.streamlit/secrets.toml
.env
.env.local
.env.*.local

# Keep templates (these ARE committed)
!.streamlit/secrets.template.toml
!.env.example
```

#### 1.5 Create Dockerfile

**New File**: `Dockerfile`

```dockerfile
FROM python:3.10-bookworm

WORKDIR /app

# System dependencies + envsubst + tini + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libssl-dev libffi-dev curl gnupg2 gettext-base tini supervisor \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy entrypoint and make executable
RUN chmod +x entrypoint.sh

# Default to non-strict locally; ECS can set STRICT_STARTUP=true
ENV STRICT_STARTUP=false

# Health check (optional - useful for ECS)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Let tini handle signals properly (PID 1)
ENTRYPOINT ["/usr/bin/tini", "--", "./entrypoint.sh"]

# Default command (can be overridden)
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Key Features**:
- Uses `tini` as PID 1 for proper signal handling
- Includes `gettext-base` for `envsubst` support
- Health check endpoint for ECS health monitoring
- Entrypoint handles secrets rendering before Streamlit starts

---

## Phase 2: ECS Fargate Configuration

### ECS Task Definition Structure

Your ECS Task Definition will inject secrets from HashiCorp Vault via environment variables:

```json
{
  "family": "trading-sheet-applet",
  "containerDefinitions": [
    {
      "name": "trading-app",
      "image": "xxx.dkr.ecr.region.amazonaws.com/trading-sheet-applet:latest",
      "essential": true,
      "environment": [
        {"name": "STRICT_STARTUP", "value": "true"},
        {"name": "TRADE_API_ENVIRONMENT", "value": "uat"},
        {"name": "AUTH_PROVIDER", "value": "secrets"},
        {"name": "TRADE_PROTECTION_BLOCK_NON_UT", "value": "true"},
        {"name": "TRADE_PROTECTION_MODE", "value": "strict"}
      ],
      "secrets": [
        {"name": "EMAIL_ADDRESS", "valueFrom": "arn:aws:secretsmanager:region:account:secret:trading/EMAIL_ADDRESS"},
        {"name": "EMAIL_APP_PASSWORD", "valueFrom": "arn:aws:secretsmanager:region:account:secret:trading/EMAIL_APP_PASSWORD"},
        {"name": "TRADE_API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:trading/TRADE_API_KEY"},
        {"name": "LLM_GEMINI_API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:trading/LLM_GEMINI_API_KEY"},
        {"name": "USERS_ADMIN_DON_EE", "valueFrom": "arn:aws:secretsmanager:region:account:secret:trading/USERS_ADMIN_DON_EE"}
      ],
      "portMappings": [
        {"containerPort": 8501, "protocol": "tcp"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8501/_stcore/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/trading-sheet-applet",
          "awslogs-region": "region",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "1024",
  "memory": "2048",
  "taskRoleArn": "arn:aws:iam::account:role/TradingAppTaskRole",
  "executionRoleArn": "arn:aws:iam::account:role/TradingAppExecutionRole"
}
```

### IAM Permissions Required

**Execution Role** (for pulling secrets at task startup):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "kms:Decrypt"
      ],
      "Resource": [
        "arn:aws:secretsmanager:region:account:secret:trading/*",
        "arn:aws:kms:region:account:key/your-kms-key-id"
      ]
    }
  ]
}
```

### HashiCorp Vault Integration

Your DevOps team can sync secrets from HashiCorp Vault to AWS Secrets Manager using:

1. **Vault Agent**: Automatic sync to AWS Secrets Manager
2. **Terraform**: `vault_generic_secret` -> `aws_secretsmanager_secret` resources
3. **CI/CD Pipeline**: Vault CLI -> AWS Secrets Manager on deployment

**Example Terraform**:

```hcl
# Read from HashiCorp Vault
data "vault_generic_secret" "trading_api_key" {
  path = "secret/trading-sheet-applet/trade_api_key"
}

# Write to AWS Secrets Manager
resource "aws_secretsmanager_secret" "trading_api_key" {
  name = "trading/TRADE_API_KEY"
  description = "Trade Allocations API Bearer Token"
}

resource "aws_secretsmanager_secret_version" "trading_api_key" {
  secret_id     = aws_secretsmanager_secret.trading_api_key.id
  secret_string = data.vault_generic_secret.trading_api_key.data["value"]
}
```

---

## Phase 3: Local Development Workflow

### Setup (One-time per developer)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Fill in your local development secrets
nano .env  # or your preferred editor

# 3. Make entrypoint executable
chmod +x entrypoint.sh

# 4. Load environment and test
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh echo "Secrets configured successfully"
```

### Daily Development

**Option 1: Using entrypoint (recommended)**

```bash
# Load environment variables
set -a; source .env; set +a

# Run application (entrypoint handles secrets)
./entrypoint.sh streamlit run app/main.py
```

**Option 2: Direct Streamlit (uses existing secrets.toml)**

```bash
# If you already have a working .streamlit/secrets.toml
streamlit run app/main.py
```

**Option 3: Docker Compose**

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    env_file: .env
    environment:
      - STRICT_STARTUP=false
      - OVERWRITE_SECRETS=true
    volumes:
      - ./app:/app/app
      - ./assets:/app/assets
```

Run with:
```bash
docker-compose up
```

---

## Variable Mapping Reference

### Critical Secrets (Required in Production)

| Environment Variable | HashiCorp Vault Path | Description |
|---------------------|---------------------|-------------|
| `EMAIL_APP_PASSWORD` | `secret/trading/email_app_password` | Gmail app-specific password |
| `TRADE_API_KEY` | `secret/trading/trade_api_key` | Trade Allocations API Bearer token |
| `LLM_GEMINI_API_KEY` | `secret/trading/llm_gemini_key` | Gemini API key (optional) |
| `USERS_ADMIN_*` | `secret/trading/users/admin_*` | Admin user credentials (pipe-delimited) |

### Configuration (Non-Sensitive)

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `EMAIL_ADDRESS` | `trading@easyequities.co.za` | Sender email address |
| `EMAIL_NOTIFICATION_ADDRESS` | `trading-ops@easyequities.co.za` | Audit email recipient |
| `TRADE_API_ENVIRONMENT` | `uat` | API environment (uat/qa/prod) |
| `TRADE_API_SYSTEM_ID` | `27` | System identifier for API |
| `TRADE_PROTECTION_BLOCK_NON_UT` | `true` | Enforce UT-only trading |
| `AUTH_PROVIDER` | `secrets` | Authentication provider |
| `AUTH_SESSION_TIMEOUT` | `60` | Session timeout (minutes) |
| `AUTH_MAX_LOGIN_ATTEMPTS` | `5` | Max failed login attempts |

### User Format

Admin users use pipe-delimited format:

```bash
USERS_ADMIN_<IDENTIFIER>="email|name|password_hash|role|enabled"

# Example:
USERS_ADMIN_DON_EE="don@easyequities.co.za|Don Kruger|$2b$12$...|admin|true"
```

**To generate a password hash**:
```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'YourPassword', bcrypt.gensalt()).decode())"
```

---

## Security Considerations

### 1. Repository Security

✅ **NEVER commit**:
- `.streamlit/secrets.toml` (generated at runtime)
- `.env` (local development secrets)
- Any file containing actual secrets

✅ **ALWAYS commit**:
- `.streamlit/secrets.template.toml` (templates with placeholders)
- `entrypoint.sh` (rendering script)
- `.env.example` (example without real secrets)

### 2. Password Hash Security

- User password hashes contain special characters (`$`)
- In `.env` files: Escape `$` as `\$` or use single quotes
- In HashiCorp Vault: Store raw hash (no escaping needed)
- In AWS Secrets Manager: Store raw hash (automatic escaping)

**Example .env format**:
```bash
# Double quotes with escaped $
USERS_ADMIN_JOHN="john@example.com|John Doe|\$2b\$12\$abc123...|admin|true"

# OR single quotes (no escaping needed)
USERS_ADMIN_JOHN='john@example.com|John Doe|$2b$12$abc123...|admin|true'
```

### 3. Production Hardening

**ECS Task Definition must set**:
```json
{"name": "STRICT_STARTUP", "value": "true"}
{"name": "TRADE_PROTECTION_BLOCK_NON_UT", "value": "true"}
{"name": "TRADE_PROTECTION_MODE", "value": "strict"}
{"name": "TRADE_PROTECTION_ALLOW_OVERRIDE", "value": "false"}
```

### 4. Least Privilege IAM

- Task Execution Role: Only read secrets at startup
- Task Role: No secrets access (application doesn't need AWS SDK)
- Restrict Secrets Manager access to specific ARN patterns

---

## Migration Steps

### Step 1: Preparation (No Downtime)

```bash
# 1. Create template from current secrets
cp .streamlit/secrets.toml .streamlit/secrets.template.toml

# 2. Replace values with placeholders (manual editing)
# Change: api_key = "actual-key-123"
# To:     api_key = "${TRADE_API_KEY:-}"

# 3. Create entrypoint.sh (from this guide)

# 4. Test locally
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py
```

### Step 2: Repository Changes

```bash
# 1. Add files to repo
git add .streamlit/secrets.template.toml
git add entrypoint.sh
git add .env.example
git add Dockerfile

# 2. Update .gitignore
git add .gitignore

# 3. Remove tracked secrets
git rm --cached .streamlit/secrets.toml

# 4. Commit and push
git commit -m "feat: implement DevOps-friendly secrets management"
git push origin main
```

### Step 3: DevOps Configuration

Send to DevOps team:

```
🔐 **HashiCorp Vault Secret Configuration Request**

**Project**: Trading Sheet Applet
**Deployment**: AWS ECS Fargate

**Secrets to Configure in Vault**:

1. `trading/EMAIL_APP_PASSWORD` = <Gmail app password>
2. `trading/TRADE_API_KEY` = <Trade Allocations API bearer token>
3. `trading/LLM_GEMINI_API_KEY` = <Gemini API key>
4. `trading/USERS_ADMIN_DON_EE` = "don@easyequities.co.za|Don Kruger|<bcrypt_hash>|admin|true"

**Non-Sensitive Configuration** (can be in Task Definition environment):
- See "Variable Mapping Reference" section in docs/devops_friendly_secrets.md

**Next Steps**:
1. Store secrets in HashiCorp Vault
2. Sync to AWS Secrets Manager (if using AWS integration)
3. Update ECS Task Definition with environment variables and secrets references
4. Deploy new task definition with STRICT_STARTUP=true
```

### Step 4: Deployment & Validation

```bash
# 1. Build and push Docker image
docker build -t trading-sheet-applet:latest .
docker tag trading-sheet-applet:latest xxx.dkr.ecr.region.amazonaws.com/trading-sheet-applet:latest
docker push xxx.dkr.ecr.region.amazonaws.com/trading-sheet-applet:latest

# 2. Update ECS Task Definition (via Terraform/CloudFormation/Console)

# 3. Deploy new task definition

# 4. Monitor container startup logs
aws logs tail /ecs/trading-sheet-applet --follow

# Expected output:
# 🔧 Trading Sheet Applet - Starting configuration...
# 🔍 Validating critical environment variables...
# ✅ Critical validations passed
# 🔨 Rendering secrets.toml from template...
# ✅ Configured 2 admin user(s)
# ✅ Secrets configuration complete
# 🚀 Starting application...
```

---

## Troubleshooting

### Issue: "Required environment variable 'TRADE_API_KEY' is not set"

**Cause**: Secret not injected from HashiCorp Vault  
**Solution**:
1. Verify secret exists in Vault: `vault kv get secret/trading/trade_api_key`
2. Check AWS Secrets Manager: `aws secretsmanager get-secret-value --secret-id trading/TRADE_API_KEY`
3. Verify ECS Task Definition `secrets` array includes the variable
4. Check IAM execution role has `secretsmanager:GetSecretValue` permission

### Issue: "Invalid user data format for USERS_ADMIN_DON"

**Cause**: Pipe-delimited user string malformed  
**Solution**:
- Format must be: `"email|name|hash|role|enabled"`
- Ensure password hash is properly escaped in `.env`: `\$2b\$12\$...`
- In Vault/Secrets Manager, use raw hash (no escaping)

### Issue: Container starts but shows "Configured 0 admin user(s)"

**Cause**: No `USERS_ADMIN_*` environment variables found  
**Solution**:
1. Check Task Definition includes user secret references
2. Verify environment variable name pattern: Must start with `USERS_ADMIN_`
3. Test locally: `env | grep USERS_ADMIN`

### Issue: Application can't find secrets after migration

**Cause**: Application code trying to access old key names  
**Solution**: Check `secrets.template.toml` structure matches application's usage of `st.secrets["section"]["key"]`

---

## Testing Strategy

### Unit Tests (Local)

```bash
# Test 1: Missing required secret (should fail)
unset TRADE_API_KEY
STRICT_STARTUP=true ./entrypoint.sh echo "Should fail"

# Expected: ❌ FATAL: Required environment variable 'TRADE_API_KEY' is not set.

# Test 2: Valid configuration (should succeed)
set -a; source .env; set +a
STRICT_STARTUP=true OVERWRITE_SECRETS=true ./entrypoint.sh echo "Should succeed"

# Expected: ✅ Secrets configuration complete

# Test 3: User parsing (should show user count)
./entrypoint.sh echo "Test" | grep "Configured.*admin user"

# Expected: ✅ Configured 2 admin user(s)
```

### Integration Tests (Docker)

```bash
# Test 4: Full container startup
docker build -t trading-test .
docker run --env-file .env -e STRICT_STARTUP=true -e OVERWRITE_SECRETS=true \
  trading-test ./entrypoint.sh echo "Container test"

# Test 5: Application startup
docker run --env-file .env -p 8501:8501 trading-test

# Access: http://localhost:8501
# Verify: Login page appears, authentication works
```

### Production Smoke Tests (ECS)

After deployment:

1. **Health Check**: Verify ECS tasks reach "HEALTHY" state
2. **Login Test**: Authenticate with admin user
3. **Audit Email**: Upload test trading sheet, verify email sent
4. **API Integration**: Submit test trade (UAT environment)
5. **Logs Review**: Check CloudWatch for successful startup

---

## Rollback Plan

If issues arise in production:

### Quick Rollback (Deploy Previous Task Definition)

```bash
# Revert to previous task definition revision
aws ecs update-service \
  --cluster trading-cluster \
  --service trading-service \
  --task-definition trading-sheet-applet:PREVIOUS_REVISION
```

### Emergency Fix (Bypass Entrypoint)

Temporarily override container command:

```json
{
  "containerDefinitions": [{
    "entrypoint": ["/usr/bin/tini", "--"],
    "command": ["streamlit", "run", "app/main.py"]
  }]
}
```

Then manually create `secrets.toml` via ECS Exec:

```bash
aws ecs execute-command \
  --cluster trading-cluster \
  --task <task-id> \
  --container trading-app \
  --interactive \
  --command "/bin/bash"

# In container:
cat > .streamlit/secrets.toml << 'EOF'
[trade_api]
api_key = "emergency-key"
...
EOF
```

---

## Future Enhancements

### 1. OAuth/SSO Integration

When migrating from password-based auth to OAuth:

```toml
# In secrets.template.toml
[auth]
provider = "${AUTH_PROVIDER:-oauth}"

[auth.oauth]
client_id = "${OAUTH_CLIENT_ID:-}"
client_secret = "${OAUTH_CLIENT_SECRET:-}"
redirect_uri = "${OAUTH_REDIRECT_URI:-}"
```

**Zero application code changes required** ✅

### 2. Database-Backed User Management

Replace `[users.admin]` with database connection:

```toml
[auth]
provider = "database"

[auth.database]
host = "${AUTH_DB_HOST:-}"
port = ${AUTH_DB_PORT:-5432}
database = "${AUTH_DB_NAME:-}"
username = "${AUTH_DB_USERNAME:-}"
password = "${AUTH_DB_PASSWORD:-}"
```

### 3. Multi-Region Deployment

Extend entrypoint.sh to select region-specific URLs:

```bash
REGION="${AWS_REGION:-us-east-1}"
export TRADE_API_UAT_BASE_URL="https://tradeallocationsapi-${REGION}.purple-uat.easyequities.io"
```

---

## Compliance & Audit

### Audit Trail

All secrets access is logged:

1. **HashiCorp Vault Audit Log**: Who accessed which secrets
2. **AWS CloudTrail**: ECS task secret retrieval
3. **CloudWatch Logs**: Container startup validation
4. **Application Logs**: Authentication attempts, trade submissions

### Compliance Benefits

✅ **SOC 2**: Secrets never in source control  
✅ **PCI DSS**: Encrypted secrets in transit (TLS) and at rest (Vault/KMS)  
✅ **ISO 27001**: Access control via IAM policies  
✅ **GDPR**: User data (emails) encrypted in Vault  

### Rotation Strategy

**Recommended Schedule**:
- API Keys: 90 days
- Email Passwords: 180 days
- User Passwords: On-demand (user-initiated)
- All Secrets: Immediately after personnel changes

**Rotation Process**:
1. Update secret in HashiCorp Vault
2. Sync to AWS Secrets Manager (automatic or manual)
3. ECS tasks automatically pick up new values on restart (no code changes)
4. Rolling deployment ensures zero downtime

---

## Summary

This solution design enables **DevOps-friendly secrets management** for the Trading Sheet Applet while:

✅ **Preserving all application functionality** - Zero code changes required  
✅ **Enabling HashiCorp Vault integration** - Secrets injected via environment variables  
✅ **Supporting AWS ECS Fargate** - Production-ready container deployment  
✅ **Maintaining security posture** - UT-only protection, audit trail, bcrypt authentication  
✅ **Simplifying local development** - Developers use `.env` files  
✅ **Providing fail-fast validation** - Container won't start with missing secrets  
✅ **Enabling multi-environment deployments** - Same image, different configs  

### Next Steps

1. **Review this document** with DevOps team
2. **Create template files** (.streamlit/secrets.template.toml, entrypoint.sh, .env.example)
3. **Test locally** using .env workflow
4. **Configure HashiCorp Vault** with production secrets
5. **Update ECS Task Definitions** with environment variables and secrets references
6. **Deploy to UAT** with STRICT_STARTUP=true
7. **Validate** all functionality (login, trade submission, audit emails)
8. **Promote to Production** with confidence

---

**Document Version**: 1.0  
**Last Updated**: October 4, 2025  
**Maintained By**: Trading Operations Team  
**Questions**: trading@easyequities.co.za

