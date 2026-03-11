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

# Create config directory with example config
RUN cp controller/config.example.yaml controller/config.yaml

# Expose ports:
# 8081 - Controller webhook server (receives calls FROM the game)
# 8000 - Dashboard web UI (served by Python http.server)
EXPOSE 8081 8000

# Health check - verify controller is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8081/health', timeout=2).raise_for_status()" || exit 1

# Default command: run controller in background + serve dashboard in foreground
# This keeps the container alive and serves both components
CMD python3 controller/controller.py --config controller/config.yaml & \
    cd dashboard && exec python3 -m http.server 8000
