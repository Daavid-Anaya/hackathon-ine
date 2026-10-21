FROM python:3.12.10-slim-bookworm@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/tmp

RUN python -m venv /opt/venv
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --require-hashes --only-binary=:all: --no-cache-dir -r /tmp/requirements.txt \
    && python -m pip check \
    && rm /tmp/requirements.txt

RUN groupadd --gid 1000 analyst \
    && useradd --uid 1000 --gid analyst --no-create-home analyst
WORKDIR /workspace
COPY --chown=analyst:analyst requirements.in requirements.txt ./
COPY --chown=analyst:analyst scripts/ ./scripts/
COPY --chown=analyst:analyst tests/ ./tests/
RUN mkdir -p data/raw data/processed outputs \
    && chown -R analyst:analyst /workspace

USER analyst
CMD ["python", "scripts/check_environment.py"]
