# install opencv
ARG JETPACK_VERSION="r32.5.0"
FROM registry.hub.docker.com/mdegans/l4t-base:${JETPACK_VERSION}

WORKDIR /usr/app

COPY ./src ./src
COPY settings.yaml .
COPY README.md .
COPY pyproject.toml .
COPY run.sh .


### build argumements ###
# change these here or with --build-arg FOO="BAR" at build time
ARG OPENCV_VERSION="4.5.1"
ARG OPENCV_DO_TEST="FALSE"
# note: 8 jobs will fail on Nano. Try 1 instead.
ARG OPENCV_BUILD_JOBS="8"
RUN touch .dockerenv
RUN wget -O build_opencv.sh https://github.com/mdegans/nano_build_opencv/raw/docker/build_opencv.sh
RUN /bin/bash build_opencv.sh

# required for apt-get -y to work properly:
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install ffmpeg libsm6 libxext6 -y


RUN pip install -e '.[prod]'

ENV SERVER_ADDRESS=127.0.0.1:8000
EXPOSE 8000

CMD ./run.sh jetson