import pytest

from flask import session
from flaskr.db import get_db

TEST_STOCK = 'AMZN'
TEST_SHARES = '1'

def test_results_redirect(client):
    get_response = client.get('results', follow_redirects=True)
    assert b"Welcome to StockMeetsBagel" in get_response.data

def test_stock_in_session(client, app):
    get_response = client.get('/')
    assert b"Welcome to StockMeetsBagel" in get_response.data

    post_response = client.post('/', data=dict(
            stock=TEST_STOCK,
            volume=TEST_SHARES
    ), follow_redirects=True)
    
    get_response = client.get('results', follow_redirects=True)
    assert b"Your profile has been generated." in get_response.data
    assert b"Compare Our Results" in get_response.data

    with app.app_context():
        db = get_db()
        profile = db.execute(
            'SELECT uid,profile FROM profiles WHERE profile LIKE \'%"EXPEXT": 77, "IMPDIS": 76%\';'
        ).fetchone()
        assert profile is not None
