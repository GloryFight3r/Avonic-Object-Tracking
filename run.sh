#!/bin/sh

python -m venv venv

. venv/bin/activate

if [ "$1" = "test" ]
  then
    pip install -e '.[test]'
    echo "Running tests with coverage"
    pytest --cov avonic_speaker_tracker --cov avonic_camera_api --cov microphone_api --cov web_app
else
    pip install .
fi

flask --app src/web_app run