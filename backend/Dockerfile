FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies (most don't need gcc for pre-built wheels)
RUN pip install --no-cache-dir -r requirements.txt || \
    (apt-get update && apt-get install -y gcc && \
     pip install --no-cache-dir -r requirements.txt && \
     apt-get remove -y gcc && apt-get autoremove -y)

# Install only postgresql-client if needed for migrations
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/* || true

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
