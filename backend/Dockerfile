FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# uv ships as a standalone tool; pip install is the most reliable path.
RUN pip install --no-cache-dir uv

WORKDIR /app

# Dependency-only layer for caching: install deps before copying source so
# changes to .py files do not invalidate the dep layer.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project

# Source
COPY . .
RUN uv sync --frozen

# venv lives at /opt/venv (outside /app) so the dev bind-mount cannot shadow it
ENV PATH="/opt/venv/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
