# Local Development Guide - Using secrets.toml

## 🎯 TL;DR for Developers

**Keep using your existing `.streamlit/secrets.toml` file for local development!**

The DevOps-friendly secrets system is designed for production deployments (ECS/Docker) and does **NOT** replace your local development workflow.

---

## 🏠 Local Development - Two Approaches

### Approach 1: Traditional Streamlit (Recommended for Daily Work)

**Use your existing secrets.toml file directly:**

```bash
# 1. Ensure your secrets.toml exists and has your credentials
nano .streamlit/secrets.toml

# 2. Run the app normally
streamlit run app/main.py

# That's it! No entrypoint, no environment variables needed.
```

**Advantages**:
- ✅ Simple and familiar
- ✅ Fast iteration
- ✅ No extra steps
- ✅ Works exactly as before

**File location**: `.streamlit/secrets.toml` (already in your project)

---

### Approach 2: DevOps-Style (Testing the Production Workflow)

**Use environment variables to generate secrets.toml:**

```bash
# 1. Create local environment file
cp env.example .env
nano .env  # Fill in your actual credentials

# 2. Load environment and run with entrypoint
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py

# The entrypoint generates .streamlit/secrets.toml from .env
```

**Advantages**:
- ✅ Tests production deployment workflow
- ✅ Validates environment variable mapping
- ✅ Useful for pre-deployment testing

**When to use**: Only when testing the DevOps workflow locally

---

## 🔒 File Protection Built-In

The entrypoint script **protects your existing secrets.toml**:

```bash
# From entrypoint.sh lines 68-71
if [ -f .streamlit/secrets.toml ] && [ "${OVERWRITE_SECRETS:-false}" != "true" ]; then
  echo "Using existing .streamlit/secrets.toml"
  exec "$@"  # Skip generation, use existing file
fi
```

**This means**:
- Your `secrets.toml` is **never** overwritten accidentally
- You must explicitly set `OVERWRITE_SECRETS=true` to regenerate it
- Safe to run `./entrypoint.sh` without fear of losing your file

---

## 📁 Your Project Structure

```
.streamlit/
  ├── secrets.toml          # YOUR file (keep this, use for local dev)
  ├── secrets.template.toml # Template for production (don't edit)
  └── secrets.example.toml  # Reference example (don't edit)

.env                        # Optional: for testing DevOps workflow locally
env.example                 # Template for .env file
entrypoint.sh              # Optional: for testing production workflow
```

**For daily development**: Only edit `.streamlit/secrets.toml`

---

## 🚀 Quick Start (First Time Setup)

### If you DON'T have secrets.toml yet:

**Option A - Copy from example**:
```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
nano .streamlit/secrets.toml  # Fill in your actual credentials
streamlit run app/main.py
```

**Option B - Generate from environment**:
```bash
cp env.example .env
nano .env  # Fill in your actual credentials
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py
```

### If you ALREADY have secrets.toml:

```bash
# Just keep using it!
streamlit run app/main.py
```

---

## ❓ Common Questions

### Q: Will the DevOps system delete my secrets.toml?
**A: No!** The entrypoint script explicitly checks for existing files and won't overwrite them unless you set `OVERWRITE_SECRETS=true`.

### Q: Should I commit secrets.toml to git?
**A: NO!** The file is in `.gitignore` and should never be committed. It contains your actual secrets.

### Q: What's the difference between the three .toml files?

| File | Purpose | Commit to Git? | Edit? |
|------|---------|----------------|-------|
| `secrets.toml` | Your actual secrets | ❌ NO | ✅ YES (local dev) |
| `secrets.template.toml` | Production template | ✅ YES | ❌ NO |
| `secrets.example.toml` | Reference example | ✅ YES | ❌ NO |

### Q: When do I use .env vs secrets.toml?
**A: Use `.env` only if testing the DevOps workflow.** For daily development, use `secrets.toml` directly.

### Q: What if I see "No secrets files found"?
**A: Your `secrets.toml` file doesn't exist.** Either:
1. Copy from example: `cp .streamlit/secrets.example.toml .streamlit/secrets.toml`
2. Generate from env: `OVERWRITE_SECRETS=true ./entrypoint.sh echo "Generated"`

### Q: Can I use both secrets.toml and .env?
**A: Yes!** If both exist:
- Running `streamlit run app/main.py` uses `secrets.toml`
- Running `./entrypoint.sh streamlit run...` uses `.env` (only if `OVERWRITE_SECRETS=true`)

---

## 🔄 Typical Workflow

### Daily Development (90% of the time)
```bash
# Edit code, edit secrets.toml if needed, run app
nano app/main.py
streamlit run app/main.py
```

### Testing API Configuration
```bash
# Edit secrets.toml with test credentials
nano .streamlit/secrets.toml
streamlit run app/main.py
```

### Testing DevOps Workflow (Before Production Deployment)
```bash
# Test the same workflow that will run in production
cp env.example .env
nano .env  # Add actual credentials
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh streamlit run app/main.py
```

---

## 🐳 Docker Development

If using Docker Compose for local testing:

```bash
# 1. Create .env file
cp env.example .env
nano .env  # Fill in credentials

# 2. Start container
docker-compose up

# Container uses entrypoint.sh to generate secrets.toml from .env
# Access: http://localhost:8501
```

---

## 🛡️ Security Best Practices

### ✅ DO:
- Keep your `secrets.toml` file local and secure
- Use `.env` file for testing (also local, never commit)
- Add both to `.gitignore` (already done)
- Generate new secrets for each environment (local/UAT/prod)

### ❌ DON'T:
- Commit `secrets.toml` to git
- Commit `.env` to git
- Share secrets via Slack/email
- Use production secrets in local development

---

## 📊 Summary Table

| What You Want to Do | Command | Uses Which File? |
|---------------------|---------|------------------|
| Run app locally (normal) | `streamlit run app/main.py` | `.streamlit/secrets.toml` |
| Test DevOps workflow | `./entrypoint.sh streamlit run...` | `.env` → generates `secrets.toml` |
| Run in Docker locally | `docker-compose up` | `.env` → generates `secrets.toml` |
| Deploy to production | (ECS container) | Vault env vars → generates `secrets.toml` |

---

## 🎯 Recommendation

**For your daily work, stick with the traditional approach:**

1. Keep your `.streamlit/secrets.toml` file
2. Edit it when you need to change credentials
3. Run `streamlit run app/main.py` normally
4. The DevOps system handles production deployments automatically

**The DevOps-friendly secrets system adds production deployment capabilities without changing your local development workflow.**

---

## 🆘 Troubleshooting

### "No secrets files found"

**Problem**: Streamlit can't find `secrets.toml`

**Solution**:
```bash
# Check if file exists
ls -la .streamlit/secrets.toml

# If missing, create from example
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
nano .streamlit/secrets.toml  # Add your actual credentials

# Or generate from .env
cp env.example .env
nano .env  # Add your credentials
set -a; source .env; set +a
OVERWRITE_SECRETS=true ./entrypoint.sh echo "secrets.toml generated"
```

### "My secrets.toml got overwritten"

**Problem**: File was regenerated when you didn't want it to be

**Cause**: You ran `./entrypoint.sh` with `OVERWRITE_SECRETS=true`

**Solution**:
```bash
# Don't use entrypoint for normal development
# Just run: streamlit run app/main.py

# If you lost your secrets, restore from backup or recreate
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
nano .streamlit/secrets.toml
```

---

**Questions?** See the main documentation:
- `QUICK_REFERENCE_DEVOPS_SECRETS.md` - Command cheat sheet
- `docs/devops_friendly_secrets.md` - Complete technical guide
- `MIGRATION_CHECKLIST.md` - Deployment guide
