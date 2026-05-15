FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/* \
    # SECURITY: Create a non-privileged user to run the container, preventing root execution.
    && groupadd -r appuser && useradd -r -g appuser appuser

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml requirements.txt ./
RUN uv pip install --no-cache -r requirements.txt

# SECURITY: Copy files with correct ownership to avoid layer size bloat while securing permissions
COPY --chown=appuser:appuser . .
RUN mkdir -p logs config && chown -R appuser:appuser logs config

# SECURITY: Run as non-root user
USER appuser

CMD ["python", "bot.py"]
