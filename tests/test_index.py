import pytest

TEST_STOCK = 'MSFT'
TEST_SHARES = '1'
TEST_STOCK2 = 'AAPL'
TEST_SHARES2 = '3'
TEST_ETF = 'VOO'
ENCODING = 'utf-8'

# run with `pytest`
# if that doesn't work, use `python -m pytest -vv`

def test_index(client):
    get_response = client.get('/')
    assert b"Welcome to StockMeetsBagel" in get_response.data

    # Add TEST_STOCK
    post_response = client.post('/', data=dict(
            stock=TEST_STOCK,
            volume=TEST_SHARES
    ), follow_redirects=True)
    assert b"Get My Results" in post_response.data
    assert bytes(TEST_STOCK, encoding=ENCODING) in post_response.data
    assert bytes(TEST_SHARES, encoding=ENCODING) in post_response.data
    # Add bogus stock ZZZZ
    post_response = client.post('/', data=dict(
            stock='ZZZZ',
            volume='1'
    ), follow_redirects=True)
    assert b"Invalid stock symbol: ZZZZ" in post_response.data
    
    # Add bogus volume
    post_response = client.post('/', data=dict(
            stock=TEST_STOCK2,
            volume='a'
    ), follow_redirects=True)
    assert b"Number of Shares must be a positive integer" in post_response.data
    assert bytes(TEST_STOCK2, encoding=ENCODING) not in post_response.data

    # Add humongous volume
    post_response = client.post('/', data=dict(
            stock=TEST_STOCK2,
            volume='29999313486231599000000000000000000000000000000000000'+
            '0000000000000000000000000000000000000000000000000000000000000'+
            '00000000000000000000000000000000000000000000000000000100000000'+
            '000000000000000000000000000000000000000000000000000000000000000'+
            '0000000000000000000000000000000000000000000000000000000000000000000010'
    ), follow_redirects=True)
    assert b"Number of Shares too large" in post_response.data
    assert bytes(TEST_STOCK2, encoding=ENCODING) not in post_response.data

    # Add non-positive volume
    post_response = client.post('/', data=dict(
            stock=TEST_STOCK2,
            volume='0'
    ), follow_redirects=True)
    assert b"Number of Shares must be a positive integer" in post_response.data
    assert bytes(TEST_STOCK2, encoding=ENCODING) not in post_response.data

    # Add ETF stock symbol
    post_response = client.post('/', data=dict(
            stock=TEST_ETF,
            volume='3'
    ), follow_redirects=True)
    assert bytes("Cannot process ETF: {}".format(TEST_ETF), 
        encoding=ENCODING) in post_response.data

    # Add TEST_STOCK2
    post_response = client.post('/', data=dict(
            stock=TEST_STOCK2,
            volume=TEST_SHARES2
    ), follow_redirects=True)
    assert bytes(TEST_STOCK2, encoding=ENCODING) in post_response.data
    assert bytes(TEST_SHARES2, encoding=ENCODING) in post_response.data

    # Remove TEST_STOCK
    get_response = client.get('remove/{}'.format(TEST_STOCK)
    , follow_redirects=True)
    assert b"Welcome to StockMeetsBagel" in get_response.data
    assert bytes(TEST_STOCK, encoding=ENCODING) not in get_response.data
    assert bytes(TEST_STOCK2, encoding=ENCODING) in get_response.data

    # Remove TEST_STOCK2
    get_response = client.get('remove/{}'.format(TEST_STOCK2)
    , follow_redirects=True)
    assert bytes(TEST_STOCK2, encoding=ENCODING) not in get_response.data
    assert b"Get My Results" not in get_response.data

    # Add bogus volume
    post_response = client.post('/', data=dict(
            stock=TEST_STOCK2,
            volume='a'
    ), follow_redirects=True)
    assert b"Number of Shares must be a positive integer" in post_response.data
    assert b"Get My Results" not in get_response.data

def test_about_remove(client):
    get_response = client.get('about')
    assert b"Website created by..." in get_response.data

    get_response = client.get('remove/ZZZZ',
        follow_redirects = True)
    assert b"Welcome to StockMeetsBagel" in get_response.data
    assert b"Get My Results" not in get_response.data
    
def test_app_no_config(client, app_no_test):
    get_response = client.get('about')
    assert b"Website created by..." in get_response.data
