FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV UVICORN_CMD_ARGS ""

EXPOSE 8000

# Install system-wide dependencies
RUN apt-get update && \
  apt-get install --no-install-recommends -y git curl gcc python3-dev && \
  apt-get clean autoclean && \
  apt-get autoremove --yes && \
  rm -rf /var/lib/apt/lists/*

# Create user for app
ENV APP_USER=appuser
RUN useradd --create-home $APP_USER
WORKDIR /home/$APP_USER
USER $APP_USER

# Use venv directly via PATH
ENV VENV_PATH=/home/$APP_USER/.venv/bin
ENV USER_PATH=/home/$APP_USER/.local/bin
ENV PATH="$VENV_PATH:$USER_PATH:$PATH"

RUN pip install --user --no-cache-dir poetry==1.1.13 && \
  poetry config virtualenvs.in-project true

COPY poetry.lock pyproject.toml ./


RUN poetry install --no-dev


COPY alembic.ini .
COPY app app
RUN mkdir ./file_storage

ARG CI_COMMIT_SHA=""
ENV GIT_COMMIT_SHA=${CI_COMMIT_SHA}

CMD alembic upgrade head && \
  uvicorn --host=0.0.0.0 $UVICORN_CMD_ARGS app.main:app
