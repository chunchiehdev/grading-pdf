FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for MarkItDown
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY app/ app/
COPY run.py .

# Install dependencies with uv
RUN uv venv .venv && \
    uv pip install -e . --python .venv/bin/python

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "run.py"] 