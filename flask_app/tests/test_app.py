import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../files')))

from app import app
import pytest

def test_home_route():
    tester = app.test_client()
    response = tester.get('/')
    assert response.status_code == 200
    assert b'Hello' in response.data
