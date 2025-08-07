# Use slim image for a smaller footprint
FROM python:3.13.2-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy migration files
COPY alembic/ ./alembic/
COPY alembic.ini .

# Make startup script executable
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Use startup script instead of direct uvicorn
CMD ["./start.sh"]
