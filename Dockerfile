FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ ./src/

# Install the application
RUN pip install --user --no-cache-dir .

FROM python:3.11-slim

WORKDIR /app

# Copy the installed packages from the builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src

# Set the entrypoint to the CLI tool
ENTRYPOINT ["kodex"]
CMD ["--help"]
