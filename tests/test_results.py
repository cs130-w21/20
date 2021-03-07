import pytest

from flaskr.db import get_db
import sqlite3

TEST_STOCK = 'AMZN'
TEST_SHARES = '1'
TEST_STOCK2 = 'AAPL'
TEST_SHARES2 = '3'
ENCODING = 'utf-8'

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
            'SELECT uid,profile FROM profiles WHERE profile LIKE \'%"EXPEXT": 88, "IMPDIS": 87%\';'
        ).fetchone()
        assert profile is not None
    
    get_response = client.get('/')
    assert bytes(TEST_STOCK, encoding=ENCODING) in post_response.data
    get_response = client.get('results', follow_redirects=True)
    assert b"Your profile has been generated." in get_response.data
    get_response = client.get('/')

    post_response = client.post('/', data=dict(
            stock=TEST_STOCK2,
            volume=TEST_SHARES2
    ), follow_redirects=True)
    get_response = client.get('results', follow_redirects=True)
    assert b"Your profile has been generated." in get_response.data
    assert b"Compare Our Results" in get_response.data

def test_generate_uid(client, app, monkeypatch):
    def fake_secrets_choice(sequence):
        return 'A'

    monkeypatch.setattr('secrets.choice', fake_secrets_choice)

    client.post('/', data=dict(
            stock=TEST_STOCK,
            volume=TEST_SHARES
    ), follow_redirects=True)

    with pytest.raises(sqlite3.IntegrityError) as e:
        get_response = client.get('results', follow_redirects=True)
    assert 'UNIQUE' in str(e.value)
