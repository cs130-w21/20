import pytest

TEST_STOCK = 'MSFT'
TEST_SHARES = '1'
ENCODING = 'utf-8'

# run with `pytest`
# if that doesn't work, use `python -m pytest -vv`

def test_index(client):
    get_response = client.get('/')
    assert b"Welcome to StockMeetsBagel" in get_response.data

    post_response = client.post('/', data=dict(
            stock=TEST_STOCK,
            volume=TEST_SHARES
        ), follow_redirects=True)
    assert b"Get My Results" in post_response.data
    assert bytes(TEST_STOCK, encoding=ENCODING) in post_response.data
    assert bytes(TEST_SHARES, encoding=ENCODING) in post_response.data



