# Timberborn Automation Controller + Dashboard
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY controller/requirements.txt ./controller/
RUN pip install --no-cache-dir -r controller/requirements.txt

# Copy controller code
COPY controller/ ./controller/

# Copy dashboard
COPY dashboard/ ./dashboard/

# Copy docs (for reference)
COPY docs/ ./docs/

# Expose ports:
# 8081 - Controller webhook server (receives calls FROM the game)
# 8000 - Dashboard web UI (served by Python http.server)
EXPOSE 8081 8000

# Health check - verify controller is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8081/health', timeout=2).raise_for_status()" || exit 1

# Default command: verify config exists, run controller in background + serve dashboard in foreground
# This keeps the container alive and serves both components
CMD if [ ! -f controller/config.yaml ]; then \
      echo "ERROR: controller/config.yaml not found!"; \
      echo "Please create it from the example:"; \
      echo "  cp controller/config.example.yaml controller/config.yaml"; \
      echo "Then mount it as a volume in docker-compose.yml"; \
      exit 1; \
    fi && \
    python3 controller/controller.py --config controller/config.yaml & \
    cd dashboard && exec python3 -m http.server 8000
