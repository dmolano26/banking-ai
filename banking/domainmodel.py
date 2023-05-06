# coding=utf-8

from hashlib import sha512
from uuid import UUID

from eventsourcing.domain import Aggregate, event

from banking.utils.custom_exceptions import (
    AccountClosedError,
    InsufficientFundsError,
    BadCredentials,
)


class Account(Aggregate):
    """
    This is the model of the aggregate, it has
    many events that happen, and when you load
    a model using the application object (Bank)
    you get all events saved for the id of the
    individual model. This never saves itself,
    all saving happens in the Bank application.
    """

    _id: UUID

    @event("Opened")
    def __init__(
        self,
        id: UUID,
        full_name: str,
        email_address: str,
        password: str,
    ):
        self._id = id
        self.full_name = full_name
        self.email_address = email_address
        self.hashed_password = sha512(password.encode("utf-8")).hexdigest()
        self.balance = 0
        self.is_closed = False

    @event("Closed")
    def close_account(self) -> None:
        self.is_closed = True

    def check_if_closed(self) -> None:
        if self.is_closed:
            raise AccountClosedError(self._id)

    def authenticate(self, email_address: str, password: str) -> None:
        hashed_password = sha512(password.encode()).hexdigest()

        if (
            self.email_address != email_address
            or self.hashed_password != hashed_password
        ):
            raise BadCredentials(email_address)
        return True

    @event("Debited")
    def debit(self, amount_in_cents: int) -> None:
        """aggregate to debit

        Args:
            amount_in_cents (int): mount to debit

        Raises:
            InsufficientFundsError: if the account has insufficient
            funds, it raises an error
        """
        if self.balance >= amount_in_cents:
            self.balance -= amount_in_cents
        else:
            raise InsufficientFundsError(self.balance, amount_in_cents)

    @event("Credited")
    def credit(self, amount_in_cents: int) -> None:
        """aggregate to get a credit

        Args:
            amount_in_cents (int): mount you want to get as a credit
        """
        self.balance += amount_in_cents
