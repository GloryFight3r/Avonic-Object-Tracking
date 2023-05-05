source venv/bin/activate
python -m build
pip instal .
pip install -e '.[test]'

cd src/web_app
flask run
