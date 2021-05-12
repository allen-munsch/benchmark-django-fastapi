FROM python:3.8.10-slim as base
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y gcc libffi-dev g++ libpq-dev python3-venv python3-wheel git curl telnet
WORKDIR /app
FROM base as builder
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
RUN python -m venv /venv

# doesn't work in 3.6.13?
#RUN . /venv/bin/activate && pip install -U "pip"
RUN . /venv/bin/activate && curl https://bootstrap.pypa.io/get-pip.py | python -

RUN . /venv/bin/activate && pip install cython wheel
# copies the current directory to the container
COPY . .
RUN . /venv/bin/activate && pip install -r /app/requirements.txt

FROM base as final
COPY --from=builder /venv /venv
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.8.0/wait /wait

RUN chmod +x /wait