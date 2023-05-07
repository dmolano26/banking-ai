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
        """Constructor, create a new account

        Args:
            id (UUID)
            full_name (str)
            email_address (str)
            password (str)
        """
        self._id = id
        self.full_name = full_name
        self.email_address = email_address
        self.hashed_password = sha512(password.encode("utf-8")).hexdigest()
        self.balance = 0
        self.is_closed = False
        self._overdraft_limit = 0

    def get_overdraft_limit(self) -> int:
        """Get the overdraft limit for the account

        Returns:
            int
        """
        return self._overdraft_limit

    @event("SetOverdraftLimit")
    def set_overdraft_limit(self, amount: int) -> None:
        """Set the overdraft limit for the account

        Args:
            amount (int)

        Raises:
            AssertionError
        """
        if amount < 0:
            raise AssertionError("Overdraft limit cannot be negative")
        self._overdraft_limit = amount

    @event("Closed")
    def close_account(self) -> None:
        """Close an existing account"""
        self.is_closed = True

    def check_if_closed(self) -> None:
        """Check if the account is closed

        Raises:
            AccountClosedError
        """
        if self.is_closed:
            raise AccountClosedError(self._id)

    @event("PasswordChanged")
    def change_password(self, new_password: str) -> None:
        """Change the password to the account

        Args:
            new_password (str)
        """
        new_hashed_password = sha512(new_password.encode()).hexdigest()
        self.hashed_password = new_hashed_password

    def authenticate(self, email_address: str, password: str) -> bool:
        """Function used to make the authentication of the account

        Args:
            email_address (str)
            password (str)

        Raises:
            BadCredentials

        Returns:
            bool
        """
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
            amount_in_cents (int)

        Raises:
            InsufficientFundsError
        """
        if amount_in_cents < 0:
            raise ValueError("Amount to debit can't be less than 0")

        if self.balance + self._overdraft_limit >= amount_in_cents:
            self.balance -= amount_in_cents
        else:
            raise InsufficientFundsError(self.balance, amount_in_cents)

    @event("Credited")
    def credit(self, amount_in_cents: int) -> None:
        """aggregate to get a credit

        Args:
            amount_in_cents (int)
        """
        self.balance += amount_in_cents
