FROM balenalib/jetson-nano-ubuntu-python:latest-build

WORKDIR /usr/app

COPY ./src ./src
COPY settings.yaml .
COPY README.md .
COPY pyproject.toml .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y && \
    pip install -e '.[prod]'

ENV SERVER_ADDRESS=0.0.0.0:8000
EXPOSE 8000

CMD while true
    do
        uwsgi --http :8000 --gevent 1000 --http-websockets --master --module web_app.wsgi:app
        echo "Restarting app in 1 second"
        sleep 1
    done