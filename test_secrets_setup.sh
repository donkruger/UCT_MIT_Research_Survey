#!/usr/bin/env bash
# =============================================================================
# Test script for DevOps-friendly secrets implementation
# Run this to validate your setup before deployment
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Testing DevOps-Friendly Secrets Implementation"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# =============================================================================
# Test 1: Check required files exist
# =============================================================================
echo "Test 1: Checking required files..."

if [ -f ".streamlit/secrets.template.toml" ]; then
    pass "secrets.template.toml exists"
else
    fail "secrets.template.toml missing"
fi

if [ -f ".streamlit/secrets.example.toml" ]; then
    pass "secrets.example.toml exists"
else
    fail "secrets.example.toml missing"
fi

if [ -f "entrypoint.sh" ]; then
    pass "entrypoint.sh exists"
else
    fail "entrypoint.sh missing"
fi

if [ -x "entrypoint.sh" ]; then
    pass "entrypoint.sh is executable"
else
    fail "entrypoint.sh is not executable (run: chmod +x entrypoint.sh)"
fi

if [ -f "env.example" ]; then
    pass "env.example exists"
else
    fail "env.example missing"
fi

if [ -f "Dockerfile" ]; then
    pass "Dockerfile exists"
else
    fail "Dockerfile missing"
fi

if [ -f "docker-compose.yml" ]; then
    pass "docker-compose.yml exists"
else
    fail "docker-compose.yml missing"
fi

echo ""

# =============================================================================
# Test 2: Check .gitignore configuration
# =============================================================================
echo "Test 2: Checking .gitignore configuration..."

if git check-ignore -q .streamlit/secrets.toml 2>/dev/null; then
    pass "secrets.toml is ignored by git"
else
    warn "secrets.toml is NOT ignored by git (should be in .gitignore)"
fi

if git check-ignore -q .env 2>/dev/null; then
    pass ".env is ignored by git"
else
    warn ".env is NOT ignored by git (should be in .gitignore)"
fi

# Check that templates are NOT ignored
if git check-ignore -q .streamlit/secrets.template.toml 2>/dev/null; then
    warn "secrets.template.toml is ignored (should be committed)"
else
    pass "secrets.template.toml will be committed"
fi

echo ""

# =============================================================================
# Test 3: Validate template structure
# =============================================================================
echo "Test 3: Validating template structure..."

if grep -q "\[email_credentials\]" .streamlit/secrets.template.toml; then
    pass "Template has [email_credentials] section"
else
    fail "Template missing [email_credentials] section"
fi

if grep -q "\[trade_api\]" .streamlit/secrets.template.toml; then
    pass "Template has [trade_api] section"
else
    fail "Template missing [trade_api] section"
fi

if grep -q "\[trade_protection\]" .streamlit/secrets.template.toml; then
    pass "Template has [trade_protection] section"
else
    fail "Template missing [trade_protection] section"
fi

if grep -q "\[auth\]" .streamlit/secrets.template.toml; then
    pass "Template has [auth] section"
else
    fail "Template missing [auth] section"
fi

if grep -q "\[users.admin\]" .streamlit/secrets.template.toml; then
    pass "Template has [users.admin] section"
else
    fail "Template missing [users.admin] section"
fi

echo ""

# =============================================================================
# Test 4: Check environment variable placeholders
# =============================================================================
echo "Test 4: Checking environment variable placeholders..."

if grep -q '${EMAIL_APP_PASSWORD' .streamlit/secrets.template.toml; then
    pass "EMAIL_APP_PASSWORD placeholder found"
else
    fail "EMAIL_APP_PASSWORD placeholder missing"
fi

if grep -q '${TRADE_API_KEY' .streamlit/secrets.template.toml; then
    pass "TRADE_API_KEY placeholder found"
else
    fail "TRADE_API_KEY placeholder missing"
fi

if grep -q '${AUTH_PROVIDER' .streamlit/secrets.template.toml; then
    pass "AUTH_PROVIDER placeholder found"
else
    fail "AUTH_PROVIDER placeholder missing"
fi

echo ""

# =============================================================================
# Test 5: Test entrypoint script execution (dry run)
# =============================================================================
echo "Test 5: Testing entrypoint script (non-strict mode)..."

# IMPORTANT: Backup existing secrets.toml if it exists
SECRETS_BACKUP=""
if [ -f ".streamlit/secrets.toml" ]; then
    SECRETS_BACKUP=".streamlit/secrets.toml.test-backup-$$"
    cp .streamlit/secrets.toml "$SECRETS_BACKUP"
    echo "ℹ️  Backed up existing secrets.toml to $SECRETS_BACKUP"
fi

# Set minimal environment for test
export STRICT_STARTUP=false
export EMAIL_ADDRESS="test@example.com"
export EMAIL_APP_PASSWORD="test-password"
export EMAIL_NOTIFICATION_ADDRESS="notify@example.com"
export TRADE_API_ENVIRONMENT="uat"
export TRADE_API_KEY="test-api-key"
export AUTH_PROVIDER="secrets"
export USERS_ADMIN_TEST="test@example.com|Test User|\$2b\$12\$abcdefghijklmnopqrstuvwxyz|admin|true"

# Test entrypoint in non-strict mode
if OVERWRITE_SECRETS=true ./entrypoint.sh echo "Test successful" > /dev/null 2>&1; then
    pass "Entrypoint executes without errors (non-strict mode)"
else
    fail "Entrypoint failed in non-strict mode"
fi

# Check if secrets.toml was generated
if [ -f ".streamlit/secrets.toml" ]; then
    pass "secrets.toml generated successfully"
    
    # Validate generated content
    if grep -q "test@example.com" .streamlit/secrets.toml; then
        pass "Generated secrets.toml contains email configuration"
    else
        warn "Generated secrets.toml may be incomplete"
    fi
    
    # Clean up generated test file
    rm .streamlit/secrets.toml
    
    # Restore original secrets.toml if it existed
    if [ -n "$SECRETS_BACKUP" ] && [ -f "$SECRETS_BACKUP" ]; then
        mv "$SECRETS_BACKUP" .streamlit/secrets.toml
        echo "ℹ️  Restored original secrets.toml"
    fi
else
    fail "secrets.toml was not generated"
fi

echo ""

# =============================================================================
# Test 6: Test strict mode validation
# =============================================================================
echo "Test 6: Testing strict mode validation..."

# Backup existing secrets.toml again (in case it was restored)
SECRETS_BACKUP_2=""
if [ -f ".streamlit/secrets.toml" ]; then
    SECRETS_BACKUP_2=".streamlit/secrets.toml.test-backup2-$$"
    cp .streamlit/secrets.toml "$SECRETS_BACKUP_2"
fi

# Unset a required variable
unset TRADE_API_KEY

# This should fail
if STRICT_STARTUP=true OVERWRITE_SECRETS=true ./entrypoint.sh echo "Should fail" > /dev/null 2>&1; then
    fail "Strict mode should have failed with missing TRADE_API_KEY"
else
    pass "Strict mode correctly validates required variables"
fi

# Restore original secrets.toml if it existed
if [ -n "$SECRETS_BACKUP_2" ] && [ -f "$SECRETS_BACKUP_2" ]; then
    mv "$SECRETS_BACKUP_2" .streamlit/secrets.toml
    rm -f "$SECRETS_BACKUP_2"
fi

echo ""

# =============================================================================
# Test 7: Check Docker configuration
# =============================================================================
echo "Test 7: Checking Docker configuration..."

if grep -q "ENTRYPOINT.*tini.*entrypoint.sh" Dockerfile; then
    pass "Dockerfile uses tini and entrypoint.sh"
else
    warn "Dockerfile may not be using tini or entrypoint.sh correctly"
fi

if grep -q "HEALTHCHECK" Dockerfile; then
    pass "Dockerfile has health check configured"
else
    warn "Dockerfile missing health check (optional but recommended)"
fi

if grep -q "ENV STRICT_STARTUP" Dockerfile; then
    pass "Dockerfile sets STRICT_STARTUP environment variable"
else
    warn "Dockerfile should set STRICT_STARTUP default"
fi

echo ""

# =============================================================================
# Test 8: Validate documentation
# =============================================================================
echo "Test 8: Checking documentation..."

if [ -f "docs/devops_friendly_secrets.md" ]; then
    pass "Implementation guide exists"
else
    fail "docs/devops_friendly_secrets.md missing"
fi

if [ -f "MIGRATION_CHECKLIST.md" ]; then
    pass "Migration checklist exists"
else
    fail "MIGRATION_CHECKLIST.md missing"
fi

if [ -f "docs/DEVOPS_SECRETS_QUICK_START.md" ]; then
    pass "Quick start guide exists"
else
    warn "Quick start guide missing (optional)"
fi

echo ""

# =============================================================================
# Test 9: Check for sensitive data leaks
# =============================================================================
echo "Test 9: Checking for sensitive data leaks..."

# Check if actual secrets.toml exists (should not be in repo)
if [ -f ".streamlit/secrets.toml" ]; then
    if git ls-files --error-unmatch .streamlit/secrets.toml 2>/dev/null; then
        fail "CRITICAL: secrets.toml is tracked by git!"
    else
        warn "secrets.toml exists locally but is not tracked (OK for development)"
    fi
else
    pass "No secrets.toml in working directory"
fi

# Check if .env exists (should not be in repo)
if [ -f ".env" ]; then
    if git ls-files --error-unmatch .env 2>/dev/null; then
        fail "CRITICAL: .env is tracked by git!"
    else
        warn ".env exists locally but is not tracked (OK for development)"
    fi
else
    pass "No .env in working directory"
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo "=================================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Copy env.example to .env and fill in your credentials"
echo "2. Run: set -a; source .env; set +a"
echo "3. Run: OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py"
echo "4. Test the application thoroughly"
echo "5. Follow MIGRATION_CHECKLIST.md for deployment"
echo ""
echo "For detailed instructions, see:"
echo "- docs/devops_friendly_secrets.md"
echo "- MIGRATION_CHECKLIST.md"
echo "- docs/DEVOPS_SECRETS_QUICK_START.md"
echo ""
