FROM python:3.13.15-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STL_GATEWAY_HOST=0.0.0.0 \
    STL_OLLAMA=http://ollama:11434

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml requirements-lock.txt README.md ./
COPY stl ./stl
RUN pip install -e ".[dev]" -c requirements-lock.txt

COPY tests ./tests
COPY results ./results

EXPOSE 8050 8025 8026

CMD ["sh", "-c", "python -m stl.cli download --checkpoints && exec python -m stl.cli serve --host 0.0.0.0"]
