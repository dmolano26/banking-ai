import pytest
from flask_jwt_extended import create_access_token

from banking.api import app
from banking.applicationmodel import Bank


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def access_token():
    bank = Bank()
    account_id = bank.get_account_id_by_email("diego.molano25@gmail.com")
    with app.test_request_context():
        access_token = create_access_token(identity=str(account_id))
        print("=======access_token====", access_token)
        yield access_token


@pytest.fixture
def destination_account_id():
    bank = Bank()
    with app.test_request_context():
        account_id = bank.open_account("Bob2", "bob2@example.com", "testpass")
        yield account_id
