import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import flask_mysqldb
flask_mysqldb.MySQL = MagicMock()

from app import app

@pytest.fixture
def client():
    # Patch MySQL to avoid real DB connection

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        yield client
