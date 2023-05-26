FROM balenalib/jetson-nano-ubuntu-python:latest-build

WORKDIR /usr/app

COPY ./src ./src
COPY README.md .
COPY pyproject.toml .

RUN python -m venv venv && \
    pip install -e '.[prod]'

ENV SERVER_ADDRESS=0.0.0.0:8000
ENV CAM_IP=1
ENV CAM_PORT=1
ENV MIC_IP=1
ENV MIC_PORT=1
ENV MIC_THRESH=-55
ENV SECRET_KEY=test

EXPOSE 8000

CMD uwsgi --http :8000 --gevent 1000 --http-websockets --master --module web_app