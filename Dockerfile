FROM balenalib/jetson-nano-ubuntu-python:latest-build

WORKDIR /usr/app

COPY ./src ./src
COPY README.md .
COPY pyproject.toml .
COPY run.sh .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y && \
    pip install -e '.[prod]'

ENV SERVER_ADDRESS=127.0.0.1:8000
ENV NO_FOOTAGE=true
EXPOSE 8000

CMD ./run.sh jetson
