#!/bin/sh

python -m venv venv

. venv/bin/activate

if [ "$1" = "test" ]
  then
    pip install -e '.[test]'
    echo "Running tests with coverage"
    pytest --cov
else
    pip install .
fi

flask --app src/web_app/app.py run
