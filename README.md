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
