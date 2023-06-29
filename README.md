# MaAT

`dev branch:` ![dev pylint](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/dev/raw/public/badges/pylint.svg?job=pylint) ![dev coverage](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/dev/raw/coverage-badge.svg?job=test)

`main branch:` ![main pylint](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/main/raw/public/badges/pylint.svg?job=pylint) ![main coverage](https://gitlab.ewi.tudelft.nl/cse2000-software-project/2022-2023-q4/ta-cluster/cluster-11/11c-avonic/11c-avonic/-/jobs/artifacts/main/raw/coverage-badge.svg?job=test)

### Microphone array Avonic Tracker
Track speakers with a camera using a microphone array

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
To build the docker container, run:

`# docker build -t maat .`

After that, run the container:

`# docker run -it --rm -p 80:8000 -v $(pwd)/config:/usr/app/config maat`