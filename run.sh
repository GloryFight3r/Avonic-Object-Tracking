#!/bin/sh

python -m venv venv

. venv/bin/activate

if [ "$1" = "test" ]
  then
    pip install -e '.[test]'
    echo "Running tests with coverage"
    pytest --cov --cov-report term --cov-report=html:pytest-html
    flask --app src/web_app run --debug
elif [ "$1" = "prod" ]
  then
    export SERVER_ADDRESS=0.0.0.0:8000
    pip install -e '.[prod]'
    uwsgi --http :8000 --gevent 1000 --http-websockets --master --module web_app
else
    pip install .
    flask --app src/web_app run
fi
