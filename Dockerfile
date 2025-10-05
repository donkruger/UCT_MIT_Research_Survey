FROM python:3.10-bookworm

WORKDIR /app

# System dependencies + envsubst + tini + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libssl-dev libffi-dev curl gnupg2 gettext-base tini \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Default to non-strict locally; ECS can set STRICT_STARTUP=true
ENV STRICT_STARTUP=false

# Health check (optional - useful for ECS)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose Streamlit port
EXPOSE 8501

# Let tini handle signals properly (PID 1)
ENTRYPOINT ["/usr/bin/tini", "--", "./entrypoint.sh"]

# Default command (can be overridden)
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
