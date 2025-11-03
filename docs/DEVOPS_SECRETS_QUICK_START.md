# DevOps-Friendly Secrets - Quick Start Guide

## For Developers (Local Development)

### First-Time Setup

```bash
# 1. Copy environment template
cp env.example .env

# 2. Edit with your credentials (get from team lead)
nano .env

# 3. Load environment variables
set -a; source .env; set +a

# 4. Generate secrets and run
OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py
```

### Daily Development

```bash
# Option 1: Use entrypoint (regenerates secrets from env)
set -a; source .env; set +a
./entrypoint.sh streamlit run app/main.py

# Option 2: Direct run (uses existing secrets.toml)
streamlit run app/main.py
```

### Testing Changes

```bash
# Test with Docker
docker-compose up

# Access: http://localhost:8501
```

---

## For DevOps (Production Deployment)

### Required Environment Variables Checklist

**CRITICAL:** All environment variables must be set in the ECS Task Definition. The template no longer contains default values.

#### Secrets (Store in Vault/Secrets Manager)

```
EMAIL_APP_PASSWORD              # Gmail app-specific password
TRADE_API_KEY                   # Trade Allocations API bearer token
LLM_GEMINI_API_KEY             # Gemini API key (optional but must be set)
USERS_ADMIN_USER_1             # "email|name|hash|role|enabled"
USERS_ADMIN_USER_2             # "email|name|hash|role|enabled" (optional)
```

#### Configuration Variables (Set in ECS environment array)

```
# Email Configuration
EMAIL_ADDRESS=trading@easyequities.co.za
EMAIL_NOTIFICATION_ADDRESS=trading-ops@easyequities.co.za
EMAIL_RECIPIENT_ADDRESS=trading-ops@easyequities.co.za
EMAIL_SMTP_SERVER=smtp.gmail.com

# Trade API Configuration
TRADE_API_ENVIRONMENT=uat
TRADE_API_UAT_BASE_URL=https://tradeallocationsapi.purple-uat.easyequities.io
TRADE_API_UAT_MONITOR_URL=https://trade-allocations-monitor.purple-uat.easyequities.io
TRADE_API_QA_BASE_URL=https://tradeallocationsapi.purple-qa.easyequities.io
TRADE_API_QA_MONITOR_URL=https://trade-allocations-monitor.purple-qa.easyequities.io
TRADE_API_PROD_BASE_URL=https://tradeallocationsapi.easyequities.io
TRADE_API_PROD_MONITOR_URL=https://trade-allocations-monitor.easyequities.io
TRADE_API_SYSTEM_ID=27
TRADE_API_TIMEOUT=30
TRADE_API_MAX_RETRIES=3
TRADE_API_POLLING_INTERVAL=5
TRADE_API_MAX_POLLING_DURATION=300
TRADE_API_DEFAULT_TRADER_ID=45314

# Trade Protection
TRADE_PROTECTION_BLOCK_NON_UT=true
TRADE_PROTECTION_PREFIX_1=UT.ZA
TRADE_PROTECTION_MODE=strict
TRADE_PROTECTION_AUDIT_ALL=true
TRADE_PROTECTION_ALLOW_OVERRIDE=false
TRADE_PROTECTION_MAX_ATTEMPTS=3

# Authentication
AUTH_PROVIDER=secrets
AUTH_SESSION_TIMEOUT=60
AUTH_INACTIVITY_TIMEOUT=30
AUTH_MAX_LOGIN_ATTEMPTS=5
AUTH_LOCKOUT_DURATION=15
AUTH_LOG_ATTEMPTS=true
AUTH_LOG_FAILED_ONLY=false

# Startup Configuration
STRICT_STARTUP=true
OVERWRITE_SECRETS=true
```

### HashiCorp Vault Configuration

Store these secrets in Vault under `secret/trading-sheet-applet/`:

```
email_app_password          # Gmail app-specific password
trade_api_key              # Trade Allocations API bearer token
llm_gemini_api_key         # Gemini API key
users/admin_user_1         # "email|name|hash|role|enabled"
users/admin_user_2         # "email|name|hash|role|enabled"
```

**IMPORTANT:** Store values WITHOUT quotes. Example:
```
# CORRECT:
don@easyequities.co.za|Don Kruger|$2b$12$...|admin|true

# WRONG (will cause parsing errors):
'don@easyequities.co.za|Don Kruger|$2b$12$...|admin|true'
```

### ECS Task Definition

**Environment Variables** (non-sensitive):
```json
{
  "environment": [
    {"name": "STRICT_STARTUP", "value": "true"},
    {"name": "TRADE_API_ENVIRONMENT", "value": "uat"},
    {"name": "TRADE_API_SYSTEM_ID", "value": "27"},
    {"name": "AUTH_PROVIDER", "value": "secrets"},
    {"name": "TRADE_PROTECTION_BLOCK_NON_UT", "value": "true"},
    {"name": "TRADE_PROTECTION_MODE", "value": "strict"}
  ]
}
```

**Secrets** (from Vault/Secrets Manager):
```json
{
  "secrets": [
    {"name": "EMAIL_APP_PASSWORD", "valueFrom": "arn:aws:secretsmanager:..."},
    {"name": "TRADE_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
    {"name": "LLM_GEMINI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
    {"name": "USERS_ADMIN_DON_EE", "valueFrom": "arn:aws:secretsmanager:..."}
  ]
}
```

### Deployment Steps

```bash
# 1. Build image
docker build -t trading-sheet-applet:latest .

# 2. Tag for ECR
docker tag trading-sheet-applet:latest <ecr-repo>:latest

# 3. Push to ECR
docker push <ecr-repo>:latest

# 4. Update ECS service
aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment
```

### Validation

Check CloudWatch logs for:
```
✅ Secrets configuration complete
✅ Configured X admin user(s)
🚀 Starting application...
```

---

## Common Tasks

### Adding a New User

**Local Development**:
```bash
# 1. Generate bcrypt hash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'NewPassword', bcrypt.gensalt()).decode())"

# 2. Add to .env
echo "USERS_ADMIN_NEW='new@example.com|New User|$2b$12$...|admin|true'" >> .env

# 3. Regenerate secrets
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh echo "User added"
```

**Production**:
1. Add secret to Vault: `secret/trading/users/admin_new`
2. Update ECS Task Definition with new secret reference
3. Deploy new task definition

### Rotating Secrets

**Local Development**:
```bash
# 1. Update value in .env
nano .env

# 2. Regenerate secrets
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py
```

**Production**:
1. Update secret in Vault
2. Restart ECS tasks (they'll pull new value automatically)

### Troubleshooting

**"Required environment variable not set"**
- Check `.env` file exists and is loaded
- Verify variable name matches `env.example`
- For production: Check ECS Task Definition has the variable

**"No admin users configured"**
- Ensure at least one `USERS_ADMIN_*` variable exists
- Check format: `email|name|hash|role|enabled`
- Verify bcrypt hash is properly escaped (use single quotes in .env)

**"Invalid user data format"**
- Format must be: `email|name|password_hash|role|enabled`
- Example: `user@ex.com|Name|$2b$12$abc...|admin|true`
- **CRITICAL:** Store in Vault WITHOUT quotes (quotes become part of the value)

**"Error parsing secrets file: Unbalanced quotes"**
- User credentials in Vault have extra single/double quotes
- Remove ALL quotes from Vault values
- Correct format: `email|name|hash|role|enabled` (no surrounding quotes)

**"This float doesn't have a leading digit" or literal `${VAR}` in secrets.toml**
- Environment variable not set in ECS Task Definition
- Check CloudWatch logs for "⚠️ WARNING: Found unsubstituted environment variables"
- Ensure `OVERWRITE_SECRETS=true` is set
- Verify ALL required variables are in the ECS Task Definition

**envsubst Limitation (IMPORTANT)**
- `envsubst` does NOT support bash default syntax: `${VAR:-default}`
- Template now uses simple `${VAR}` placeholders only
- ALL environment variables MUST be explicitly set in ECS
- No fallback defaults - missing variables will cause startup failure in strict mode

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HashiCorp Vault                          │
│                   (Secrets Storage)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Sync (automated)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                AWS Secrets Manager                          │
│            (ECS-accessible secrets)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Inject at runtime
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ECS Task Definition                        │
│   environment: [non-sensitive config]                      │
│   secrets: [sensitive values from Secrets Manager]         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Container startup
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    entrypoint.sh                            │
│   1. Validate required variables                           │
│   2. Render secrets.template.toml → secrets.toml          │
│   3. Start Streamlit application                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Application reads
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Streamlit Application                       │
│   st.secrets["section"]["key"]                             │
│   (No code changes required!)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Best Practices

✅ **DO**:
- Use `STRICT_STARTUP=true` in production
- Store all secrets in HashiCorp Vault
- Use bcrypt hashes for passwords (never plaintext)
- Set `TRADE_PROTECTION_ALLOW_OVERRIDE=false` in production
- Monitor CloudWatch logs for security events
- Rotate secrets every 90 days

❌ **DON'T**:
- Commit `.env` or `secrets.toml` to repository
- Share secrets via Slack/email (use secure channels)
- Disable strict mode in production
- Hard-code secrets in code or config files
- Use weak passwords for admin users
- Skip testing after secrets rotation

---

## Resources

- **Full Implementation Guide**: `docs/devops_friendly_secrets.md`
- **Migration Checklist**: `MIGRATION_CHECKLIST.md`
- **Environment Example**: `env.example`
- **Secrets Template**: `.streamlit/secrets.template.toml`

**Need Help?**
- Technical Support: trading@easyequities.co.za
- DevOps Team: See internal wiki for contact
