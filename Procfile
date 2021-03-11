worker: flask init-db
web: waitress-serve --port=$PORT --call 'flaskr:create_app'
