import pytest

TEST_ID1 = 'DEEPFKNVAL'
TEST_ID2 = 'A1B2C3D4E5'
ENCODING = 'utf-8'

def test_get_compare(client):
    get_response = client.get('compare/<placeholder>', follow_redirects=True)
    assert b"Compare Portfolios" in get_response.data

def test_post_compare(client):
    # Enter same ID
    post_response = client.post('compare/<placeholder>', data=dict(
            person1=TEST_ID1,
            person2=TEST_ID1
    ), follow_redirects=True)
    assert b"Compare Portfolios" in post_response.data
    assert b"IDs cannot be the same!" in post_response.data

    # test if IDs are invalid/have no DB entries
    post_response = client.post('compare/<placholder>', data=dict(
            person1=TEST_ID1,
            person2='ZZZZZZZZZZ'
    ), follow_redirects=True)
    assert b"Compare Portfolios" in post_response.data
    assert b"Invalid ID" in post_response.data

    post_response = client.post('compare/<placholder>', data=dict(
            person1='ZZZZZZZZZZ',
            person2=TEST_ID1
    ), follow_redirects=True)
    assert b"Compare Portfolios" in post_response.data
    assert b"Invalid ID" in post_response.data
    # Enter two IDs
    
    # no portfolio in session, so should redirect to index
    post_response = client.post('compare/<placeholder>', data=dict(
            person1=TEST_ID1,
            person2=TEST_ID2
    ), follow_redirects=True)
    assert b"Your Compatibility is" in post_response.data

def test_post_compare2(client):
    # check for incomplete 
    post_response = client.post('compare/<placeholder>', data=dict(
        person1='BBBBBBBBBB',
        person2=TEST_ID2
    ), follow_redirects=True)
    assert b"Your Compatibility is" in post_response.data

    post_response = client.post('compare/<placeholder>', data=dict(
        person1=TEST_ID1,
        person2='BBBBBBBBBB'
    ), follow_redirects=True)
    assert b"Your Compatibility is" in post_response.data
    # same hobbie
    post_response = client.post('compare/<placeholder>', data=dict(
        person1=TEST_ID2,
        person2='AAAAAAAAAA'
    ), follow_redirects=True)
    assert b"Your Compatibility is" in post_response.data

def test_compare_with_code(client):
    get_response = client.get('compare/AAAAAAAAAA', follow_redirects=True)
    assert b"Compare Portfolios" in get_response.data
    assert b"AAAAAAAAAA" in get_response.data
