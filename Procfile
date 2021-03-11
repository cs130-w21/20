init: export FLASK_APP=flaskr && flask init-db
web: waitress-serve --port=$PORT --call 'flaskr:create_app'
