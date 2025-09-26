import pytest
from files.app import app  # import from your Flask app module

def test_home_route():
    # Use the Flask test client
    tester = app.test_client()

    # Make a GET request to the home route
    response = tester.get('/')

    # Assert that the response status code is 200
    assert response.status_code == 200

    # Assert that the response contains expected content
    assert b'Hello' in response.data
