# Use the official Python image.
FROM python:3.13-slim

# Set the working directory in the container.
WORKDIR /app

ENV PYTHONPATH /app

# Install uv and postgresql-client (for pg_dump/pg_restore)
RUN pip install uv && apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy dependency definition files first for better caching.
COPY pyproject.toml uv.lock ./

# Install production dependencies only.
RUN uv sync --no-dev

# Copy the rest of the project files into the container.
COPY . ./

# Expose the port the app runs on.
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.paypulse.main:app", "--host", "0.0.0.0", "--port", "8000"]
