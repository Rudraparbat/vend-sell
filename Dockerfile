# ---- Base Stage ----
FROM python:3.13-slim AS base


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# ---- Builder Stage ----
# This stage installs dependencies, including build tools
FROM base AS builder

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ---- Final Stage ----
FROM base AS final

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy the installed Python packages from the builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*


# Set the working directory
WORKDIR /app

# Copy the application code from your local machine to the container
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















# # Stage 1: builder (has build tools)
# FROM python:3.13.2-slim-bookworm AS builder
# WORKDIR /app

# # System packages only for building wheels (not in final)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     build-essential \
#     libpq-dev \
#   && rm -rf /var/lib/apt/lists/*

# # Copy only dependency manifests first to leverage Docker cache
# COPY requirements.txt .

# # Create a venv for dependencies
# RUN python -m venv /opt/venv \
#   && . /opt/venv/bin/activate \
#   && pip install --upgrade pip \
#   && pip install --no-cache-dir -r requirements.txt
# # --no-cache-dir prevents pip wheel/http cache from bloating the layer[10][7][13].

# # Stage 2: runtime (no compilers, lean)
# FROM python:3.13.2-slim-bookworm AS runtime
# WORKDIR /app

# # Minimal system runtime deps only (psql client optional)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     postgresql-client \
#   && rm -rf /var/lib/apt/lists/*

# # Copy app code
# COPY . .

# # Copy venv from builder
# COPY --from=builder /opt/venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH" \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# # Copy migrations if they are not already in .
# # (Your COPY . . likely already includes alembic/ and alembic.ini)

