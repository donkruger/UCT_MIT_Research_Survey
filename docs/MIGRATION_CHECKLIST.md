# DevOps-Friendly Secrets Migration Checklist

This checklist guides you through migrating from hardcoded `secrets.toml` to the DevOps-friendly secrets management system.

## ⚠️ Pre-Migration Safety Checks

- [ ] **Backup current secrets**: `cp .streamlit/secrets.toml .streamlit/secrets.toml.backup`
- [ ] **Verify application is working**: Test login, file upload, and trade submission
- [ ] **Document current state**: Note all working features for post-migration validation
- [ ] **Review existing secrets**: Confirm all sections in current secrets.toml

## 📋 Phase 1: Local Testing Setup

### Step 1: Verify New Files Exist

- [ ] `.streamlit/secrets.template.toml` exists
- [ ] `.streamlit/secrets.example.toml` exists
- [ ] `entrypoint.sh` exists and is executable (`chmod +x entrypoint.sh`)
- [ ] `env.example` exists
- [ ] `Dockerfile` exists
- [ ] `docker-compose.yml` exists
- [ ] `.gitignore` updated to allow templates

### Step 2: Create Local Environment File

```bash
# Copy the example environment file
cp env.example .env

# Edit with your actual credentials
nano .env  # or your preferred editor
```

**Fill in these CRITICAL values**:
- [ ] `EMAIL_APP_PASSWORD` - Your Gmail app-specific password
- [ ] `TRADE_API_KEY` - Your Trade Allocations API bearer token
- [ ] `LLM_GEMINI_API_KEY` - Your Gemini API key (if using AI features)
- [ ] `USERS_ADMIN_*` - At least one admin user with bcrypt hash

**Example user format**:
```bash
USERS_ADMIN_DON_EE='don@easyequities.co.za|Don Kruger|$2b$12$reMoGR/59jGtr/KIirPNE.exovMzGd4vZsDaoJf/JopaUe3jAXz.W|admin|true'
```

### Step 3: Test Entrypoint Script Locally

```bash
# Load environment variables
set -a; source .env; set +a

# Test with strict mode OFF (should show warnings only)
STRICT_STARTUP=false OVERWRITE_SECRETS=true ./entrypoint.sh echo "Test successful"

# Expected output:
# 🔧 Trading Sheet Applet - Starting configuration...
# 🔍 Validating critical environment variables...
# ⚠️  WARNING: Optional environment variable 'EMAIL_ADDRESS' is not set (non-strict mode).
# [... more warnings if any ...]
# ✅ Critical validations passed
# 🔨 Rendering secrets.toml from template...
# ✅ Configured X admin user(s)
# ✅ Secrets configuration complete
# 🚀 Starting application...
# Test successful
```

**Validation**:
- [ ] No FATAL errors appeared
- [ ] User count matches expected (e.g., "Configured 2 admin user(s)")
- [ ] `.streamlit/secrets.toml` was created

### Step 4: Verify Generated Secrets File

```bash
# Check the generated secrets.toml structure
cat .streamlit/secrets.toml | head -20
```

**Verify**:
- [ ] `[email_credentials]` section exists with your email
- [ ] `[trade_api]` section exists with API key
- [ ] `[trade_protection]` section has `block_non_ut_trades = true`
- [ ] `[auth]` section has `provider = "secrets"`
- [ ] `[users.admin]` section has your admin user(s) with bcrypt hashes

### Step 5: Test Application with Generated Secrets

```bash
# Method 1: Using entrypoint (recommended)
set -a; source .env; set +a
./entrypoint.sh streamlit run app/main.py

# Method 2: Direct run (using generated secrets.toml)
streamlit run app/main.py
```

**Test These Features**:
- [ ] Application starts without errors
- [ ] Login page appears with proper branding
- [ ] Can log in with admin credentials
- [ ] Session timeout works (check after 30+ min inactivity)
- [ ] Rate limiting works (try 5+ failed logins)
- [ ] Declaration page loads
- [ ] File upload interface works
- [ ] Can preview uploaded CSV/Excel files
- [ ] Submit page shows API configuration
- [ ] UT-only protection is enforced
- [ ] Audit email system works (test with small CSV)

### Step 6: Test with Strict Mode

```bash
# Test strict validation (should fail if critical secrets missing)
unset TRADE_API_KEY
STRICT_STARTUP=true ./entrypoint.sh echo "Should fail"

# Expected: ❌ FATAL: Required environment variable 'TRADE_API_KEY' is not set.
```

**Validation**:
- [ ] Script exits immediately with clear error message
- [ ] Exit code is non-zero (`echo $?` should show 1)

### Step 7: Test Docker Build (Optional but Recommended)

```bash
# Build Docker image
docker build -t trading-sheet-applet-test .

# Test with environment file
docker run --rm --env-file .env -p 8501:8501 trading-sheet-applet-test

# Access: http://localhost:8501
```

**Validation**:
- [ ] Docker build completes successfully
- [ ] Container starts and shows configuration messages
- [ ] Application accessible at http://localhost:8501
- [ ] All features work same as local testing

### Step 8: Test Docker Compose (Full Stack)

```bash
# Ensure .env file exists and is populated
# Then start the stack
docker-compose up

# In another terminal, check logs
docker-compose logs -f trading-app
```

**Validation**:
- [ ] Container builds successfully
- [ ] Secrets rendered correctly in logs
- [ ] Application starts and is accessible
- [ ] Health check passes (check with `docker-compose ps`)

## 📋 Phase 2: Repository Changes

⚠️ **CRITICAL**: Only proceed if Phase 1 testing was 100% successful!

### Step 9: Prepare Repository

```bash
# Check current git status
git status

# Verify secrets.toml is still ignored
git check-ignore .streamlit/secrets.toml
# Should output: .streamlit/secrets.toml

# Verify templates are NOT ignored (should be committed)
git check-ignore .streamlit/secrets.template.toml
# Should output: (nothing - means it will be committed)
```

### Step 10: Stage New Files

```bash
# Add new DevOps-friendly files
git add .streamlit/secrets.template.toml
git add .streamlit/secrets.example.toml
git add entrypoint.sh
git add env.example
git add Dockerfile
git add docker-compose.yml
git add .gitignore
git add docs/devops_friendly_secrets.md
git add MIGRATION_CHECKLIST.md

# Verify secrets.toml is NOT staged
git status | grep secrets.toml
# Should only show secrets.template.toml and secrets.example.toml
```

**Double-check**:
- [ ] `secrets.toml` is NOT in staged files
- [ ] `.env` is NOT in staged files (if you created one)
- [ ] Only templates and examples are staged

### Step 11: Commit Changes

```bash
# Commit with descriptive message
git commit -m "feat: implement DevOps-friendly secrets management

- Add secrets template with environment variable placeholders
- Add entrypoint.sh for runtime secrets rendering
- Add Dockerfile and docker-compose.yml for containerization
- Add comprehensive migration guide and documentation
- Update .gitignore to protect secrets while allowing templates

Implements HashiCorp Vault compatibility for ECS deployment.
Zero application code changes - maintains full backward compatibility."

# Review commit
git show --stat
```

**Verify commit**:
- [ ] Commit includes only safe files (templates, scripts, docs)
- [ ] No secrets.toml in commit
- [ ] No .env file in commit
- [ ] entrypoint.sh has correct permissions (executable)

### Step 12: Push to Repository

```bash
# Push to remote (use appropriate branch)
git push origin main  # or your branch name

# Verify on GitHub/GitLab
# Check that secrets.toml is not visible in repository
```

## 📋 Phase 3: DevOps Configuration

### Step 13: Prepare DevOps Request

Send this information to your DevOps team:

```
🔐 HashiCorp Vault Configuration Request
Project: Trading Sheet Applet
Deployment Target: AWS ECS Fargate

CRITICAL SECRETS (store in HashiCorp Vault):
1. trading/email_app_password = <Gmail app-specific password>
2. trading/trade_api_key = <Trade Allocations API bearer token>
3. trading/llm_gemini_api_key = <Gemini API key>
4. trading/users/admin_don_ee = "don@easyequities.co.za|Don Kruger (EasyEquities)|<bcrypt_hash>|admin|true"
5. trading/users/admin_don_ec = "don@easycrypto.co.za|Don Kruger (EasyCrypto)|<bcrypt_hash>|admin|true"

NON-SENSITIVE CONFIGURATION (can be in Task Definition):
- TRADE_API_ENVIRONMENT=uat
- TRADE_API_SYSTEM_ID=27
- AUTH_PROVIDER=secrets
- TRADE_PROTECTION_BLOCK_NON_UT=true
- TRADE_PROTECTION_MODE=strict
- STRICT_STARTUP=true  # REQUIRED for production

Full variable mapping: See docs/devops_friendly_secrets.md

ECS Task Definition Requirements:
- Execution Role: secretsmanager:GetSecretValue permission
- Environment variables: Non-sensitive config
- Secrets: Sensitive values from Vault/Secrets Manager
- Health check: /api/health or /_stcore/health

Reference Documentation:
- docs/devops_friendly_secrets.md
- MIGRATION_CHECKLIST.md (this file)
```

**Checklist**:
- [ ] DevOps team has received request
- [ ] Vault paths confirmed
- [ ] AWS Secrets Manager sync configured (if applicable)
- [ ] IAM roles created/updated

### Step 14: ECS Task Definition Configuration

Work with DevOps to configure:

**Required Environment Variables**:
- [ ] `STRICT_STARTUP=true`
- [ ] `TRADE_API_ENVIRONMENT=uat` (or qa/prod)
- [ ] `TRADE_PROTECTION_BLOCK_NON_UT=true`
- [ ] `TRADE_PROTECTION_MODE=strict`
- [ ] `AUTH_PROVIDER=secrets`

**Required Secrets** (from Vault/Secrets Manager):
- [ ] `EMAIL_ADDRESS`
- [ ] `EMAIL_APP_PASSWORD`
- [ ] `EMAIL_NOTIFICATION_ADDRESS`
- [ ] `TRADE_API_KEY`
- [ ] `LLM_GEMINI_API_KEY`
- [ ] `USERS_ADMIN_*` (one or more admin users)

**Task Definition Settings**:
- [ ] Health check configured: `curl -f http://localhost:8501/_stcore/health`
- [ ] Port mapping: 8501
- [ ] CPU/Memory: At least 1024 CPU, 2048 Memory
- [ ] Log configuration: CloudWatch logs enabled

### Step 15: Deploy to UAT

```bash
# Build production image
docker build -t <ecr-repo>:latest .

# Tag for ECR
docker tag <ecr-repo>:latest <account>.dkr.ecr.<region>.amazonaws.com/trading-sheet-applet:latest

# Push to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker push <account>.dkr.ecr.<region>.amazonaws.com/trading-sheet-applet:latest

# Update ECS service (via Terraform/CloudFormation/Console)
```

**Validation**:
- [ ] ECS task starts successfully
- [ ] CloudWatch logs show: "✅ Secrets configuration complete"
- [ ] CloudWatch logs show: "✅ Configured X admin user(s)"
- [ ] Health check passes (task status: HEALTHY)
- [ ] No FATAL errors in logs

### Step 16: Post-Deployment Testing (UAT)

Access the UAT application and test:

- [ ] Application loads without errors
- [ ] Login page displays correctly
- [ ] Can authenticate with admin credentials
- [ ] Session management works (timeout, lockout)
- [ ] Declaration page loads
- [ ] File upload works (test with sample CSV)
- [ ] Data validation works (try invalid data)
- [ ] UT-only protection enforced (try non-UT contract code)
- [ ] Trade submission works (submit to UAT API)
- [ ] Polling/status monitoring works
- [ ] Audit email received after submission
- [ ] Email contains correct user identity
- [ ] CSV attachment included in email

### Step 17: Validate Secrets Security

**Check CloudWatch logs for**:
- [ ] No plaintext secrets visible in logs
- [ ] No password hashes visible in logs
- [ ] No API keys visible in logs
- [ ] Only masked or redacted sensitive data

**Check ECS Task Definition**:
- [ ] Secrets injected via `secrets` array (not `environment`)
- [ ] Secrets reference Vault ARNs (not plaintext values)
- [ ] Task Execution Role has proper permissions

**Check Application Behavior**:
- [ ] `st.secrets["email_credentials"]["app_password"]` works
- [ ] `st.secrets["trade_api"]["api_key"]` works
- [ ] `st.secrets["users"]["admin"]` contains bcrypt hashes

## 📋 Phase 4: Production Deployment

⚠️ **STOP**: Only proceed if UAT testing is 100% successful!

### Step 18: Production Secrets Configuration

- [ ] DevOps: Update Vault with production secrets
- [ ] DevOps: Create production AWS Secrets Manager entries
- [ ] DevOps: Configure production ECS Task Definition
- [ ] DevOps: Set `STRICT_STARTUP=true` (REQUIRED)
- [ ] DevOps: Set `TRADE_PROTECTION_ALLOW_OVERRIDE=false` (REQUIRED)
- [ ] DevOps: Set `TRADE_API_ENVIRONMENT=prod`

### Step 19: Deploy to Production

```bash
# Tag production release
git tag -a v1.0.0-devops-secrets -m "Production release with DevOps-friendly secrets"
git push origin v1.0.0-devops-secrets

# Build production image (from tagged release)
docker build -t <ecr-repo>:v1.0.0 .
docker push <account>.dkr.ecr.<region>.amazonaws.com/trading-sheet-applet:v1.0.0

# Deploy to production ECS (via your deployment pipeline)
```

**Validation**:
- [ ] Production task starts successfully
- [ ] CloudWatch logs confirm secrets loaded
- [ ] Health check passes
- [ ] No errors in startup logs

### Step 20: Production Smoke Tests

**Critical Tests**:
- [ ] Application accessible via production URL
- [ ] SSL/TLS certificate valid
- [ ] Login works with production credentials
- [ ] Authentication rate limiting works
- [ ] Session timeout enforced
- [ ] File upload works
- [ ] Trade submission to production API works
- [ ] Audit emails sent to correct addresses
- [ ] User identity captured correctly in emails

### Step 21: Monitor for 24 Hours

**Monitor CloudWatch**:
- [ ] No authentication errors
- [ ] No API connection failures
- [ ] No secrets loading errors
- [ ] Normal application performance

**Monitor ECS**:
- [ ] Task remains healthy
- [ ] No unexpected restarts
- [ ] Memory/CPU usage normal

**Monitor Application**:
- [ ] Users can log in consistently
- [ ] Trade submissions succeeding
- [ ] Audit emails being sent

## 📋 Phase 5: Cleanup & Documentation

### Step 22: Clean Up Local Development

```bash
# Remove backup if everything works
rm .streamlit/secrets.toml.backup

# Keep .streamlit/secrets.toml for local dev
# (It's in .gitignore, so it won't be committed)

# Ensure .env is in .gitignore
git check-ignore .env
# Should output: .env
```

### Step 23: Update Team Documentation

- [ ] Add to team wiki: "How to set up local environment"
- [ ] Document: "How to add new secrets"
- [ ] Document: "How to rotate secrets in production"
- [ ] Update onboarding docs for new developers
- [ ] Share env.example with team (via secure channel)

### Step 24: Developer Onboarding Documentation

Create team guide with:

```markdown
## Local Development Setup

1. Clone repository
2. Copy env.example to .env
3. Get credentials from team lead (via secure channel)
4. Load environment: `set -a; source .env; set +a`
5. Run: `./entrypoint.sh streamlit run app/main.py`
6. Access: http://localhost:8501
```

## 🚨 Rollback Plan

If anything goes wrong:

### Immediate Rollback (Production)

```bash
# Option 1: Revert to previous ECS task definition
aws ecs update-service \
  --cluster trading-cluster \
  --service trading-service \
  --task-definition trading-sheet-applet:PREVIOUS_REVISION

# Option 2: Emergency fix - manually add secrets.toml to container
aws ecs execute-command \
  --cluster trading-cluster \
  --task <task-id> \
  --container trading-app \
  --interactive \
  --command "/bin/bash"

# In container: Copy from backup or recreate manually
```

### Code Rollback (Repository)

```bash
# Revert the commit
git revert <commit-hash>
git push origin main

# OR reset to previous state (use with caution)
git reset --hard HEAD~1
git push --force origin main  # Coordinate with team!
```

## ✅ Success Criteria

Migration is successful when:

- [x] All Phase 1 tests pass (local testing)
- [x] All Phase 2 steps complete (repository changes)
- [x] All Phase 3 validations pass (UAT deployment)
- [x] All Phase 4 checks pass (production deployment)
- [x] 24-hour monitoring shows no issues
- [x] Team can set up local development
- [x] DevOps team can rotate secrets
- [x] No secrets visible in repository or logs

## 📚 Additional Resources

- **Implementation Guide**: `docs/devops_friendly_secrets.md`
- **Reference Project**: `docs/AVA_reference_files/`
- **Adding New Secrets**: `docs/AVA_reference_files/Adding_new_secrets_playbook_example.md`
- **README**: Updated with DevOps secrets information

## 🆘 Troubleshooting

### Issue: "Required environment variable not set"

**Solution**: Check `.env` file has all required variables from `env.example`

### Issue: "No admin users configured"

**Solution**: Ensure at least one `USERS_ADMIN_*` variable in `.env` with correct pipe-delimited format

### Issue: "Invalid user data format"

**Solution**: Check format: `email|name|hash|role|enabled` - ensure bcrypt hash is properly escaped

### Issue: Container starts but app doesn't load

**Solution**: Check CloudWatch logs for Python errors; ensure secrets.toml structure matches application's expectations

### Issue: Authentication not working

**Solution**: Verify bcrypt hashes are correct; test hash generation locally

---

**Document Version**: 1.0  
**Last Updated**: October 5, 2025  
**Contact**: trading@easyequities.co.za
