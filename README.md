# SpeakerSense

`dev branch:` ![dev pylint](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/dev/raw/public/badges/pylint.svg?job=pylint) ![dev coverage](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/dev/raw/coverage-badge.svg?job=test)

`main branch:` ![main pylint](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/main/raw/public/badges/pylint.svg?job=pylint) ![main coverage](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/main/raw/coverage-badge.svg?job=test)

### Track speakers with a camera using a microphone array

## Installing and running

### Locally
The easiest way to install and run the project is using the `run.sh` script,
which creates a virtual environment, downloads and installs all requirements using `pip`,
then launches the server.

To run in production mode:

`$ ./run.sh prod`

To run in development (slower, easy for debugging):

`$ ./run.sh`

To run tests:

`$ ./run.sh test`

### Docker
To build the docker container on an **ARM** (aarch64) machine, run:

`# docker build -t speakersense .`

This will take a long time (multiple hours), especially on the Jetson Nano.
On an Apple M1, it took around 30 minutes. This is because
the command compiles OpenCV, Python 3.10, and uWSGI from source.
After that, it is possible to run the container:

`# docker run -it --rm -p 80:8000 speakersense`