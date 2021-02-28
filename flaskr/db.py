import sqlite3, click, json

from flask import current_app, g
from flask.cli import with_appcontext

# API for reading/writing to sqlite db

def get_profile(user_id):
    """
    Queries SQLite database for profile by user ID

    Arguments
    ---------
    user_id : string
        User ID of profile to query

    Returns
    -------
    sqlite3.Row
        A Row object containing the query result, or
        None if a row with uid = user_id does not exist
    """

    profile = get_db().execute(
            'SELECT * FROM profiles WHERE uid = ?', (user_id,)
        ).fetchone()

    return profile

def create_profile(user_id, profile={}):
    """
    Creates a new row in the profiles table of the SQLite database

    Arguments
    ---------
    user_id : string
        User ID of profile
    profile : (strint, int) dict
        Profile containing personality factors and values
        created by algorithm.generate_profile()

    Notes
    -----
    Profile is serialized into a JSON string using json.dumps()
    before storing into the database (SQLite does not support
    storing of complex data structures)
    """

    db = get_db()
    db.execute(
        'INSERT INTO profiles (uid, profile)'
        ' VALUES (?, ?)',
        (user_id, json.dumps(profile))
    )
    db.commit()

# Tutorial code from https://flask.palletsprojects.com/en/1.1.x/tutorial/database/

def get_db():
    """
    Initializes connection to SQLite database if one hasn't already
    been created, otherwise returns the singleton Connection object

    Returns
    -------
    sqlite3.Connection
        A Connection object to the SQLite database
    """

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """Closes connection to SQLite database"""

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
