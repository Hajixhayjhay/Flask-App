import sys
import os
import pytest

# Add the 'files' folder to the Python path so we can import app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../files')))

from app import app  # now we can import app.py from files/

def test_home_route():
    tester = app.test_client()
    response = tester.get('/')
    assert response.status_code == 200
    assert b'Hello' in response.data  # adjust based on actual content in index.html.j2
