FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload"]
