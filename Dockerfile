FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
ENV UVICORN_CMD_ARGS ""

ARG NON_ROOT_USER=express_bot
RUN useradd --create-home ${NON_ROOT_USER}

EXPOSE 8000
WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN apt-get update && \
    apt-get install -y git sudo && \
    pip install poetry==1.1.0 --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    echo "${NON_ROOT_USER} ALL = NOPASSWD: /usr/sbin/update-ca-certificates" > /etc/sudoers.d/express_bot && \
    rm -rf /root/.cache/pypoetry && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY . .

USER ${NON_ROOT_USER}

CMD sudo update-ca-certificates && \
    alembic upgrade head && \
    uvicorn --host=0.0.0.0 $UVICORN_CMD_ARGS app.main:app
