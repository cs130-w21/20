import pytest

TEST_ID1 = 'DEEPFKNVAL'
TEST_ID2 = 'A1B2C3D4E5'
ENCODING = 'utf-8'

def test_get_compare(client):
    get_response = client.get('compare', follow_redirects=True)
    assert b"Compare Portfolios" in get_response.data

# PLACEHOLDER TEST
# TODO: Implement this in Sprint 3
def test_post_compare(client):
    # Enter same ID
    post_response = client.post('compare', data=dict(
            person1=TEST_ID1,
            person2=TEST_ID1
    ), follow_redirects=True)
    assert b"Compare Portfolios" in post_response.data
    assert b"IDs cannot be the same!" in post_response.data

    # test if IDs are invalid/have no DB entries
    post_response = client.post('compare', data=dict(
            person1=TEST_ID1,
            person2='ZZZZZZZZZZ'
    ), follow_redirects=True)
    assert b"Compare Portfolios" in post_response.data
    assert b"Invalid ID" in post_response.data
    # Enter two IDs
    
    # no portfolio in session, so should redirect to index
    # TODO: implement this when Compare is implemented
    post_response = client.post('compare', data=dict(
            person1=TEST_ID1,
            person2=TEST_ID2
    ), follow_redirects=True)
    assert b"Your Compatibility is" in post_response.data
