#!/bin/sh

python -m venv venv

. venv/bin/activate

if [ "$1" = "test" ]
  then
    pip install -e '.[test]'
    echo "Running tests with coverage"
    pytest --cov
    flask --app src/web_app run --debug
elif [ "$1" = "prod" ]
  then
    pip install -e '.[prod]'
    gunicorn -b 0.0.0.0 'web_app:create_app()' -k gevent -w 4
else
    pip install .
    flask --app src/web_app run
fi
