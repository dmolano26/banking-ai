# coding=utf-8
# flake8: noqa E402

import logging
import os
import typing
from uuid import UUID
from dotenv import load_dotenv

from flask import Flask, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_restful import Resource, Api

from banking.applicationmodel import Bank
from banking.utils.error_handler import error_handler


app = Flask(__name__)
load_dotenv()
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_DEFAULT_REALM"] = os.getenv("JWT_DEFAULT_REALM")
api = Api(app, prefix="/api/v1")
_bank = Bank()
jwt = JWTManager(app)


def bank() -> Bank:
    """Return a Bank App instance"""
    return _bank


class SignupResource(Resource):
    """Endpoint used to make the signup"""

    @error_handler
    def post(self) -> typing.Tuple[typing.Dict[str, str], int]:
        """POST /api/v1/signup"""
        data = request.get_json()
        account_id = bank().open_account(
            data["full_name"], data["email_address"], data["password"]
        )
        return {"account_id": str(account_id)}, 201


class LoginResource(Resource):
    """Endpoint used to make the login"""

    @error_handler
    def post(self) -> typing.Tuple[typing.Dict[str, str], int]:
        """POST /api/v1/login"""
        data = request.get_json()
        account_id = bank().authenticate(
            data["email_address"], data["password"]
        )
        access_token = create_access_token(identity=str(account_id))
        return {"access_token": access_token}, 200


class AccountResource(Resource):
    """Endpoint used to make the account information"""

    @jwt_required()
    @error_handler
    def get(self) -> typing.Dict[str, typing.Any]:
        """GET /api/v1/account"""
        logging.info("account get")
        account = bank().get_account(UUID(get_jwt_identity()))
        return {
            "balance": str(account.balance),
            "identity": get_jwt_identity(),
        }


class DepositResource(Resource):
    """Endpoint used to make the deposits to the account"""

    @jwt_required()
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        """POST /api/v1/deposit"""
        data = request.get_json()
        amount = data["amount"]
        bank().deposit_funds(UUID(get_jwt_identity()), amount)
        return {"result": "success"}


class TransferResource(Resource):
    """Endpoint used to make the transfers to other accounts"""

    @jwt_required()
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        """POST /api/v1/transfer"""
        data = request.get_json()
        amount = data["amount"]
        destination_id = UUID(data["destination_id"])
        bank().transfer_funds(UUID(get_jwt_identity()), destination_id, amount)
        return {"result": "success"}


class WithdrawResource(Resource):
    """Endpoint used to make the withdraws"""

    @jwt_required()
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        """POST /api/v1/withdraw"""
        data = request.get_json()
        amount = data["amount"]
        bank().withdraw_funds(UUID(get_jwt_identity()), amount)
        return {"result": "success"}


api.add_resource(AccountResource, "/account")
api.add_resource(SignupResource, "/signup")
api.add_resource(LoginResource, "/login")
api.add_resource(DepositResource, "/deposit")
api.add_resource(TransferResource, "/transfer")
api.add_resource(WithdrawResource, "/withdraw")
