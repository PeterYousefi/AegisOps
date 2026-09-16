# AegisOps backend — production-style container image.
# Python 3.12 to match the project target. Runs as a non-root user.

FROM python:3.12-slim AS base

# Avoid writing .pyc files and buffering stdout/stderr in containers.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first (better layer caching). Copy only the files
# needed to resolve dependencies before copying the full source.
COPY pyproject.toml ./
COPY requirements-pinned.txt ./

# Install pinned runtime dependencies.
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-pinned.txt

# Copy the application source and install the package itself (no deps again).
# NOTE: alembic.ini, migrations/, and seed/ are wired in a later task (M2);
# they are added to this image build when they exist.
COPY app ./app
COPY seed ./seed
RUN python -m pip install --no-deps -e .

# Create and switch to a non-root user.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Uvicorn serves the ASGI app defined by the app factory module-level `app`.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
