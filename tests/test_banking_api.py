import json
from uuid import uuid4

from banking.api import app
from banking.applicationmodel import Bank


def test_signup():
    client = app.test_client()

    # Sign Up Request
    data_signup = {
        "full_name": "Test User",
        "email_address": "test@test.com",
        "password": "testpass",
    }
    response_signup = client.post(
        "/api/v1/signup",
        data=json.dumps(data_signup),
        content_type="application/json",
    )
    assert response_signup.status_code == 201
    assert response_signup.json["account_id"] is not None

    # Log in Request
    data_login = {"email_address": "test@test.com", "password": "testpass"}
    response_login = client.post(
        "/api/v1/login",
        data=json.dumps(data_login),
        content_type="application/json",
    )
    assert response_login.status_code == 200
    assert response_login.json["access_token"] is not None

    # Account Request
    bearer_token = response_login.json["access_token"]
    response_account = client.get(
        "/api/v1/account", headers={"Authorization": f"Bearer {bearer_token}"}
    )
    assert response_account.status_code == 200

    # Deposit Request
    data_deposit = {"amount": 500}
    response_deposit = client.post(
        "/api/v1/deposit",
        data=json.dumps(data_deposit),
        content_type="application/json",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    assert response_deposit.status_code == 200
    assert response_deposit.json["result"] == "success"

    # Withdraw Request
    data_withdraw = {"amount": 50}
    response_withdraw = client.post(
        "/api/v1/withdraw",
        data=json.dumps(data_withdraw),
        content_type="application/json",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    assert response_withdraw.status_code == 200
    assert response_withdraw.json["result"] == "success"

    # Transfer Request
    data_user_to_transfer = {
        "full_name": "Test User Dest",
        "email_address": "testDest@test.com",
        "password": "testpass",
    }
    response_new_user_to_transfer = client.post(
        "/api/v1/signup",
        data=json.dumps(data_user_to_transfer),
        content_type="application/json",
    )
    data_transfer = {
        "amount": 5,
        "destination_id": str(
            response_new_user_to_transfer.json["account_id"]
        ),
    }
    response_transfer = client.post(
        "/api/v1/transfer",
        data=json.dumps(data_transfer),
        content_type="application/json",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    assert response_transfer.status_code == 200
    assert response_transfer.json["result"] == "success"
