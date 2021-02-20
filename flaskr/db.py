import sqlite3, click, json

from flask import current_app, g
from flask.cli import with_appcontext

# API for reading/writing to sqlite db

def get_profile(user_id):
    session = get_db().execute(
            'SELECT * FROM profiles WHERE sid = ?', (user_id,)
        ).fetchone()

    return session

def create_profile(user_id, portfolio1={}):

    db = get_db()
    db.execute(
        'INSERT INTO profiles (sid, portfolio, )'
        ' VALUES (?, ?)',
        (user_id, json.dumps(portfolio1),)
    )
    db.commit()
    return True

# Tutorial code from https://flask.palletsprojects.com/en/1.1.x/tutorial/database/

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
