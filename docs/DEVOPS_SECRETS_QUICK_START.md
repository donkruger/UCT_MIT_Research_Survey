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

### HashiCorp Vault Configuration

Store these secrets in Vault under `secret/trading-sheet-applet/`:

```
email_app_password          # Gmail app-specific password
trade_api_key              # Trade Allocations API bearer token
llm_gemini_api_key         # Gemini API key
users/admin_don_ee         # "email|name|hash|role|enabled"
users/admin_don_ec         # "email|name|hash|role|enabled"
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
- Use single quotes to avoid shell expansion of `$`

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
