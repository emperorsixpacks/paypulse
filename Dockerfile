# Use the official Python image.
FROM python:3.13-slim AS builder

WORKDIR /app
ENV PYTHONPATH=/app

# Install uv and build deps
RUN pip install uv

# Copy dependency files for caching
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --no-dev

# Runtime stage
FROM python:3.13-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source
COPY . ./

EXPOSE 8000

CMD ["uvicorn", "src.paypulse.main:app", "--host", "0.0.0.0", "--port", "8000"]
