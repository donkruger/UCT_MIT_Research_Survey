# Trading Sheet Applet - Jenkins Pipeline & AWS ECS Deployment Request

## Project Overview

**Application**: Trading Sheet Applet  
**Purpose**: Unit Trust (UT) trade processing via EasyEquities Trade Allocations API  
**Deployment Model**: AWS ECS Fargate with Docker containers  
**Pipeline Template**: Similar to EasyAI project (Jenkins → Docker → ECR → ECS)  
**Repository**: Trading Sheet Applet  
**Branch**: `main` (or specify deployment branch)

## Executive Summary

This application has been implemented with **DevOps-friendly secrets management** that aligns with your HashiCorp Vault → AWS Secrets Manager → ECS workflow. All secrets are injected as environment variables at container startup via `entrypoint.sh`, with **zero hardcoded credentials** in the repository.

### Key Implementation Features
- ✅ **Secrets template system** using environment variable substitution
- ✅ **Fail-fast validation** (`STRICT_STARTUP=true` in production)
- ✅ **Container health checks** with Streamlit health endpoint
- ✅ **Signal handling** via tini for graceful shutdowns
- ✅ **Comprehensive documentation** (see `docs/devops_friendly_secrets.md`)

---

## 1. Jenkins Pipeline Requirements

### Pipeline Stages

We request a Jenkins pipeline with the following stages, similar to the EasyAI project:

1. **Checkout** - Pull code from repository
2. **Build Docker Image** - Build container from `Dockerfile`
3. **Push to ECR** - Tag and push to AWS Elastic Container Registry
4. **Deploy to ECS** - Update ECS service with new task definition
5. **Health Check** - Verify deployment success via ECS health checks

### Build Configuration

- **Base Image**: `python:3.10-bookworm`
- **Dockerfile Location**: `./Dockerfile` (root of repository)
- **Build Context**: Repository root
- **Exposed Port**: `8501` (Streamlit default)
- **Container Entrypoint**: `["/usr/bin/tini", "--", "./entrypoint.sh"]`
- **Health Check Endpoint**: `/_stcore/health`

### Deployment Environments

Please configure pipelines for:
- **UAT Environment** - For testing and validation
- **Production Environment** - For live operations

---

## 2. HashiCorp Vault Secrets Configuration

### Vault Path Structure

Recommended Vault path: `secret/trading-sheet-applet/`

### Required Secrets (Sensitive Values)

**I will provide the actual secret values via Slack DM.** Please configure the following secret keys in HashiCorp Vault:

#### 2.1 Email Configuration (Audit Trail)
```
secret/trading-sheet-applet/email_app_password
```
- **Description**: Gmail app-specific password for SMTP authentication
- **Type**: String
- **Required**: Yes (critical for audit emails)
- **Usage**: Sends audit trail emails for all trade submissions

#### 2.2 Trade Allocations API
```
secret/trading-sheet-applet/trade_api_key
```
- **Description**: Bearer token for Trade Allocations API authentication
- **Type**: String
- **Required**: Yes (critical for core functionality)
- **Usage**: Authenticates API calls to EasyEquities Trade Allocations service

#### 2.3 LLM API (Optional)
```
secret/trading-sheet-applet/llm_gemini_api_key
```
- **Description**: Google Gemini API key for AI-assisted features
- **Type**: String
- **Required**: No (feature is optional)
- **Usage**: Powers AI assistance for trade sheet validation and help

#### 2.4 Admin User Credentials

**Format**: `email|name|password_hash|role|enabled`

```
secret/trading-sheet-applet/users/admin_user_1
secret/trading-sheet-applet/users/admin_user_2
```

**Example value structure** (actual values via Slack DM):
```
user@example.com|User Name|$2b$12$<bcrypt_hash>|admin|true
```

**Important Notes**:
- Password hashes are **bcrypt hashes**, not plain text passwords
- Use pipe `|` as delimiter with no spaces around pipes
- Store raw bcrypt hash in Vault (no escaping needed)
- At least one admin user is required for application access
- Hash format: `email|name|password_hash|role|enabled`

**Example for two users**:
```
USERS_ADMIN_USER_1 = "don@easyequities.co.za|Don Kruger (EasyEquities)|$2b$12$...|admin|true"
USERS_ADMIN_USER_2 = "don@easycrypto.co.za|Don Kruger (EasyCrypto)|$2b$12$...|admin|true"
```

---

## 3. AWS Secrets Manager Sync

Please sync HashiCorp Vault secrets to AWS Secrets Manager using your standard process (Terraform, Vault Agent, or CI/CD pipeline).

### Secrets Manager Naming Convention

Map Vault secrets to AWS Secrets Manager with the following names:

| Vault Path | AWS Secrets Manager Name | Environment Variable |
|------------|-------------------------|---------------------|
| `secret/trading-sheet-applet/email_app_password` | `trading/EMAIL_APP_PASSWORD` | `EMAIL_APP_PASSWORD` |
| `secret/trading-sheet-applet/trade_api_key` | `trading/TRADE_API_KEY` | `TRADE_API_KEY` |
| `secret/trading-sheet-applet/llm_gemini_api_key` | `trading/LLM_GEMINI_API_KEY` | `LLM_GEMINI_API_KEY` |
| `secret/trading-sheet-applet/users/admin_user_1` | `trading/USERS_ADMIN_USER_1` | `USERS_ADMIN_USER_1` |
| `secret/trading-sheet-applet/users/admin_user_2` | `trading/USERS_ADMIN_USER_2` | `USERS_ADMIN_USER_2` |

**Note**: The environment variable names must match exactly as shown in the third column, as the `entrypoint.sh` script expects these specific variable names.

---

## 4. ECS Task Definition Configuration

### 4.1 Container Definition - UAT Environment

```json
{
  "family": "trading-sheet-applet-uat",
  "containerDefinitions": [
    {
      "name": "trading-app",
      "image": "<ECR_REPOSITORY_URI>:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "STRICT_STARTUP", "value": "true"},
        {"name": "OVERWRITE_SECRETS", "value": "true"},
        {"name": "EMAIL_ADDRESS", "value": "don@easycrypto.co.za"},
        {"name": "EMAIL_NOTIFICATION_ADDRESS", "value": "don.kruger123@gmail.com"},
        {"name": "EMAIL_RECIPIENT_ADDRESS", "value": "don.kruger123@gmail.com"},
        {"name": "EMAIL_SMTP_SERVER", "value": "smtp.gmail.com"},
        {"name": "TRADE_API_ENVIRONMENT", "value": "uat"},
        {"name": "TRADE_API_UAT_BASE_URL", "value": "https://tradeallocationsapi.purple-uat.easyequities.io"},
        {"name": "TRADE_API_UAT_MONITOR_URL", "value": "https://trade-allocations-monitor.purple-uat.easyequities.io"},
        {"name": "TRADE_API_QA_BASE_URL", "value": "https://tradeallocationsapi.purple-qa.easyequities.io"},
        {"name": "TRADE_API_QA_MONITOR_URL", "value": "https://trade-allocations-monitor.purple-qa.easyequities.io"},
        {"name": "TRADE_API_PROD_BASE_URL", "value": "https://tradeallocationsapi.easyequities.io"},
        {"name": "TRADE_API_PROD_MONITOR_URL", "value": "https://trade-allocations-monitor.easyequities.io"},
        {"name": "TRADE_API_SYSTEM_ID", "value": "27"},
        {"name": "TRADE_API_TIMEOUT", "value": "30"},
        {"name": "TRADE_API_MAX_RETRIES", "value": "3"},
        {"name": "TRADE_API_POLLING_INTERVAL", "value": "5"},
        {"name": "TRADE_API_MAX_POLLING_DURATION", "value": "300"},
        {"name": "TRADE_API_DEFAULT_TRADER_ID", "value": "45314"},
        {"name": "TRADE_PROTECTION_BLOCK_NON_UT", "value": "true"},
        {"name": "TRADE_PROTECTION_PREFIX_1", "value": "UT.ZA"},
        {"name": "TRADE_PROTECTION_MODE", "value": "strict"},
        {"name": "TRADE_PROTECTION_AUDIT_ALL", "value": "true"},
        {"name": "TRADE_PROTECTION_ALLOW_OVERRIDE", "value": "false"},
        {"name": "TRADE_PROTECTION_MAX_ATTEMPTS", "value": "3"},
        {"name": "AUTH_PROVIDER", "value": "secrets"},
        {"name": "AUTH_SESSION_TIMEOUT", "value": "60"},
        {"name": "AUTH_INACTIVITY_TIMEOUT", "value": "30"},
        {"name": "AUTH_MAX_LOGIN_ATTEMPTS", "value": "5"},
        {"name": "AUTH_LOCKOUT_DURATION", "value": "15"},
        {"name": "AUTH_LOG_ATTEMPTS", "value": "true"},
        {"name": "AUTH_LOG_FAILED_ONLY", "value": "false"}
      ],
      "secrets": [
        {
          "name": "EMAIL_APP_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:trading/EMAIL_APP_PASSWORD"
        },
        {
          "name": "TRADE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:trading/TRADE_API_KEY"
        },
        {
          "name": "LLM_GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:trading/LLM_GEMINI_API_KEY"
        },
        {
          "name": "USERS_ADMIN_USER_1",
          "valueFrom": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:trading/USERS_ADMIN_USER_1"
        },
        {
          "name": "USERS_ADMIN_USER_2",
          "valueFrom": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:trading/USERS_ADMIN_USER_2"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8501/_stcore/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/trading-sheet-applet-uat",
          "awslogs-region": "<REGION>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "1024",
  "memory": "2048",
  "taskRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/TradingAppTaskRole",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/TradingAppExecutionRole"
}
```

### 4.2 Production Environment Changes

For **Production** deployment, update the following environment variables:

```json
"environment": [
  {"name": "TRADE_API_ENVIRONMENT", "value": "prod"}
]
```

Change the log group name:
```json
"awslogs-group": "/ecs/trading-sheet-applet-prod"
```

Update the task family:
```json
"family": "trading-sheet-applet-prod"
```

**All security settings remain the same** (strict mode, UT-only protection enabled).

---

## 5. Expected Startup Behavior

### 5.1 Successful Startup Logs

Upon successful deployment with all secrets configured, you should see the following in CloudWatch Logs:

```
🔧 Trading Sheet Applet - Starting configuration...
🔍 Validating critical environment variables...
✅ Critical validations passed
🔨 Rendering secrets.toml from template...
✅ Configured 2 admin user(s)
✅ Secrets configuration complete
🚀 Starting application...
```

### 5.2 Startup Failure Scenarios

**Missing Critical Secret**:
```
❌ FATAL: Required environment variable 'TRADE_API_KEY' is not set.
```
Container will exit with code 1.

**No Admin Users Configured**:
```
⚠️  WARNING: No valid admin users configured
❌ FATAL: At least one admin user required in strict mode
```
Container will exit with code 1.

**Invalid User Format**:
```
⚠️  WARNING: Invalid user data format for USERS_ADMIN_USER_1 (skipping)
```
Container may start but affected user won't be able to login.

### 5.3 Validation Logic

The `entrypoint.sh` script validates:
1. ✅ `EMAIL_ADDRESS` - Sender email for audit trail
2. ✅ `EMAIL_APP_PASSWORD` - SMTP authentication
3. ✅ `EMAIL_NOTIFICATION_ADDRESS` - Audit email recipient
4. ✅ `TRADE_API_ENVIRONMENT` - API environment (uat/qa/prod)
5. ✅ `TRADE_API_KEY` - API bearer token
6. ✅ `AUTH_PROVIDER` - Authentication method
7. ✅ At least one `USERS_ADMIN_*` variable exists

With `STRICT_STARTUP=true` (production), missing any of these will prevent container startup.

---

## Additional Information

### Documentation References

Comprehensive documentation is available in the repository:

1. **`docs/devops_friendly_secrets.md`** - Complete implementation guide (1100+ lines)
2. **`docs/DEVOPS_SECRETS_QUICK_START.md`** - Quick reference for DevOps
3. **`docs/DEVOPS_SECRETS_IMPLEMENTATION_SUMMARY.md`** - Implementation summary
4. **`docs/MIGRATION_CHECKLIST.md`** - Deployment validation checklist
5. **`env.example`** - All environment variables with descriptions
6. **`.streamlit/secrets.template.toml`** - Secrets template structure
7. **`entrypoint.sh`** - Startup script with validation logic
8. **`Dockerfile`** - Container build instructions

### Technical Specifications

- **Runtime**: Python 3.10
- **Framework**: Streamlit
- **Port**: 8501 (HTTP)
- **Health Check**: `/_stcore/health`
- **Resource Requirements**: 
  - CPU: 1 vCPU (1024 units)
  - Memory: 2 GB (2048 MB)

### Sensitive Values Transfer

**All sensitive secret values will be provided via Slack DM**, including:
- Gmail app password
- Trade API bearer token
- Gemini API key (if needed)
- Admin user password hashes (bcrypt format)

---

## Summary

This application is **production-ready** with:
- ✅ DevOps-friendly secrets management (HashiCorp Vault compatible)
- ✅ Fail-fast validation (STRICT_STARTUP=true)
- ✅ Comprehensive health checks
- ✅ Complete audit trail
- ✅ Security hardening (UT-only protection, rate limiting, session management)
- ✅ Extensive documentation

**Next Steps**:
1. Review this deployment request
2. I'll send sensitive secret values via Slack DM
3. Configure HashiCorp Vault with provided secrets
4. Sync secrets to AWS Secrets Manager
5. Create Jenkins pipeline (similar to EasyAI project)
6. Deploy to UAT environment
7. Validate deployment
8. Promote to Production after successful UAT validation

Thank you for your support in deploying this application!

