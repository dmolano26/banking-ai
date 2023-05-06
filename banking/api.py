# coding=utf-8
# flake8: noqa E402

import logging
import typing
from uuid import UUID

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
from banking.utils.custom_exceptions import AccountNotFoundError


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_DEFAULT_REALM"] = "Banking App"
api = Api(app, prefix="/api/v1")
_bank = Bank()
jwt = JWTManager(app)


def bank() -> Bank:
    return _bank


class SignupResource(Resource):
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        data = request.get_json()
        account_id = bank().open_account(
            data["full_name"], data["email_address"], data["password"]
        )
        return {"account_id": str(account_id)}, 201


class LoginResource(Resource):
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        data = request.get_json()
        account_id = bank().authenticate(
            data["email_address"], data["password"]
        )
        access_token = create_access_token(identity=str(account_id))
        return {"access_token": access_token}, 200


class AccountResource(Resource):
    @jwt_required()
    @error_handler
    def get(self) -> typing.Dict[str, typing.Any]:
        logging.info("account get")
        account = bank().get_account(UUID(get_jwt_identity()))
        return {
            "balance": str(account.balance),
            "identity": get_jwt_identity(),
        }


class DepositResource(Resource):
    @jwt_required()
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        data = request.get_json()
        amount = data["amount"]
        bank().deposit(UUID(get_jwt_identity()), amount)
        return {"result": "success"}


class TransferResource(Resource):
    @jwt_required()
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        data = request.get_json()
        amount = data["amount"]
        destination_id = UUID(data["destination_id"])
        bank().transfer(UUID(get_jwt_identity()), destination_id, amount)
        return {"result": "success"}


class WithdrawResource(Resource):
    @jwt_required()
    @error_handler
    def post(self) -> typing.Dict[str, typing.Any]:
        data = request.get_json()
        amount = data["amount"]
        bank().withdraw(UUID(get_jwt_identity()), amount)
        return {"result": "success"}


api.add_resource(AccountResource, "/account")
api.add_resource(SignupResource, "/signup")
api.add_resource(LoginResource, "/login")
api.add_resource(DepositResource, "/deposit")
api.add_resource(TransferResource, "/transfer")
api.add_resource(WithdrawResource, "/withdraw")
