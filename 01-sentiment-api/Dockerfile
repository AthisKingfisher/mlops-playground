# Start from a slim official Python image - small, official, trusted.
FROM python:3.12-slim

# Where our app will live inside the container.
WORKDIR /app

# Copy ONLY requirements first, then install. This is a caching trick:
# Docker re-runs a step only if its inputs changed. Deps change rarely,
# so this layer gets cached and rebuilds stay fast.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application code.
COPY app/ ./app/
COPY data/ ./data/

# Document the port the app listens on.
EXPOSE 8000

# The command that runs when the container starts.
# Note: no --reload here (that's a dev-only convenience).
# Host 0.0.0.0 means "listen on all interfaces" - required inside a container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]