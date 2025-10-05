# DevOps-Friendly Secrets - Quick Reference Card

## 🚀 Quick Commands

### Local Development

```bash
# First-time setup
cp env.example .env
nano .env  # Fill in your credentials

# Run application
set -a; source .env; set +a
./entrypoint.sh streamlit run app/main.py

# OR with Docker
docker-compose up
```

### Testing

```bash
# Validate setup
./test_secrets_setup.sh

# Test strict mode
STRICT_STARTUP=true OVERWRITE_SECRETS=true ./entrypoint.sh echo "Test"
```

---

## 📝 Environment Variables (Most Critical)

```bash
# Required for core functionality
EMAIL_APP_PASSWORD=your-gmail-app-password
TRADE_API_KEY=your-api-bearer-token
TRADE_API_ENVIRONMENT=uat  # or qa, prod

# Required for authentication
AUTH_PROVIDER=secrets
USERS_ADMIN_USER='email|name|$2b$12$hash|admin|true'

# Required for security
TRADE_PROTECTION_BLOCK_NON_UT=true
TRADE_PROTECTION_MODE=strict
```

See `env.example` for complete list.

---

## 🔐 User Management

### Generate Password Hash
```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'YourPassword', bcrypt.gensalt()).decode())"
```

### Add User (Local)
```bash
# In .env file (use single quotes to avoid $ escaping)
USERS_ADMIN_NEW='email@example.com|Full Name|$2b$12$hash...|admin|true'
```

### Add User (Production)
Store in Vault: `secret/trading/users/admin_new`

---

## 🐳 Docker Commands

```bash
# Build
docker build -t trading-sheet-applet .

# Run with environment
docker run --env-file .env -p 8501:8501 trading-sheet-applet

# Docker Compose
docker-compose up -d        # Start detached
docker-compose logs -f      # Follow logs
docker-compose down         # Stop
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Required env var not set" | Check `.env` has all variables from `env.example` |
| "No admin users configured" | Add at least one `USERS_ADMIN_*` variable |
| "Invalid user data format" | Format: `email\|name\|hash\|role\|enabled` |
| Container won't start | Check CloudWatch logs, verify secrets injected |
| Auth not working | Verify bcrypt hash correct, check escaping |

---

## 📁 File Structure

```
.
├── .streamlit/
│   ├── secrets.toml           # Generated (never commit)
│   ├── secrets.template.toml  # Template (commit)
│   └── secrets.example.toml   # Reference (commit)
├── entrypoint.sh              # Secrets renderer (commit)
├── env.example                # Template (commit)
├── .env                       # Local secrets (never commit)
├── Dockerfile                 # Container config (commit)
└── docker-compose.yml         # Dev stack (commit)
```

---

## 🎯 Deployment Checklist

### Before Deploying
- [ ] All Phase 1 tests pass (local)
- [ ] Docker build succeeds
- [ ] Test script passes: `./test_secrets_setup.sh`
- [ ] No secrets in `git status`

### DevOps Configuration
- [ ] Secrets in HashiCorp Vault
- [ ] ECS Task Definition updated
- [ ] `STRICT_STARTUP=true` in production
- [ ] IAM roles configured

### After Deploying
- [ ] CloudWatch shows: "✅ Secrets configuration complete"
- [ ] Application accessible
- [ ] Login works
- [ ] Trade submission works
- [ ] Audit emails sent

---

## 📚 Documentation Links

- **Full Guide**: `docs/devops_friendly_secrets.md`
- **Migration**: `MIGRATION_CHECKLIST.md`
- **Quick Start**: `docs/DEVOPS_SECRETS_QUICK_START.md`
- **Summary**: `DEVOPS_SECRETS_IMPLEMENTATION_SUMMARY.md`

---

## 🆘 Emergency Contacts

- **Technical Support**: trading@easyequities.co.za
- **DevOps Team**: See internal wiki
- **Rollback**: See `MIGRATION_CHECKLIST.md` → "Rollback Plan"

---

**Print this card** and keep it handy during migration!
