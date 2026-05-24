# ─────────────────────────────────────────────
# Dockerfile — FastAPI Backend
# Model Drift Detective
# ─────────────────────────────────────────────
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI via Uvicorn
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]