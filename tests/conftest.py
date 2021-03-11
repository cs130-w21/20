import os, pytest
import tempfile
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
	_data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
	db_fd, db_path = tempfile.mkstemp()

	app = create_app({
		'TESTING': True,
		'DATABASE': db_path,
		'SECRET_KEY': b'\x12\xf1\xca.\x15\x86\xbe\xaax\x18n<`\xe3O\x95',
	})
	with app.app_context():
		init_db()
		get_db().executescript(_data_sql)
	yield app

	os.close(db_fd)
	os.unlink(db_path)

@pytest.fixture
def app_no_test():
	app = create_app(None)
	# Warning: do not use this fixture for testing beyond
	# initialization. If you need to, initialize the 
	# DB here. (NOT RECOMMENDED)
	yield app

@pytest.fixture
def client(app):
	return app.test_client()

@pytest.fixture
def runner(app):
	return app.test_cli_runner()