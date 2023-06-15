#!/bin/sh

if [ "$1" = "jetson" ]
  then
    while true
    do
      python3 -c "\
from gevent import monkey
monkey.patch_all()
      "
      # it is recommended that you apply the monkey patching at the top of your main script, even above your imports.
      uwsgi --http :8000 --gevent 1000 --http-websockets --master --module web_app.wsgi:app
      echo "Restarting app in 1 second"
      sleep 1
    done
fi

python3 -m venv venv

. venv/bin/activate

if [ "$1" = "test" ]
  then
    pip3 install -e '.[test]'
    echo "Running tests with coverage"
    pytest --cov --cov-report term --cov-report=html:pytest-html
    flask --app src/web_app run --debug
elif [ "$1" = "prod" ]
  then
    export SERVER_ADDRESS=0.0.0.0:8000
    pip3 install -e '.[prod]'
    while true
    do
      python3 -c "\
from gevent import monkey
monkey.patch_all()
      "
      # it is recommended that you apply the monkey patching at the top of your main script, even above your imports.
      uwsgi --http :8000 --gevent 1000 --http-websockets --master --module web_app.wsgi:app
      echo "Restarting app in 1 second"
      sleep 1
    done
else
    pip3 install .
    flask --app src/web_app run
fi
