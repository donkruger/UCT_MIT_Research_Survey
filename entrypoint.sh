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

# -----------------------------------------------------------------------------
# Validate that all environment variables were substituted
# -----------------------------------------------------------------------------
echo "🔍 Checking for unsubstituted variables..."

unsubstituted=$(grep -oE '\$\{[A-Za-z_][A-Za-z0-9_]*\}' .streamlit/secrets.toml.tmp || true)

if [ -n "$unsubstituted" ]; then
  echo "⚠️  WARNING: Found unsubstituted environment variables:" >&2
  echo "$unsubstituted" | sort -u | sed 's/^/    /' >&2
  
  if [ "${STRICT_STARTUP}" = "true" ]; then
    echo "❌ FATAL: Unsubstituted variables found in strict mode" >&2
    echo "    Set all required environment variables in ECS Task Definition" >&2
    exit 1
  else
    echo "    Continuing in non-strict mode (these will appear as literals in config)" >&2
  fi
else
  echo "✅ All environment variables substituted successfully"
fi

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
