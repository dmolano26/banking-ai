# coding=utf-8

from uuid import NAMESPACE_URL, UUID, uuid5

from eventsourcing.application import AggregateNotFound, Application

from banking.domainmodel import Account
from banking.utils.custom_exceptions import (
    BadCredentials,
    TransactionError,
    AccountNotFoundError,
)


class Bank(Application):
    """
    This is the model of the application, it has
    all of its events in the from of aggregate
    events that it loads. This loads and
    saves aggregates and forms the business logic
    for reading and writing.

    To create an aggregate run:
      new_account = Account(...)

    To load existing aggregates run:
      account1 = self.repository.get(account_id1)
      account2 = self.repository.get(account_id2)

    To save any aggregates run:
      self.save(account1, account2, new_account)
    """

    def open_account(
        self,
        full_name: str,
        email_address: str,
        password: str,
    ) -> UUID:
        """Function used to open a new acount using the /signup endpoint

        Args:
            full_name (str): Full name of the owner
            email_address (str): email of the owner
            password (str): password used to interact with the account

        Returns:
            UUID: unique identifier of the account
        """
        account = Account(
            self.get_account_id_by_email(email_address),
            full_name=full_name,
            email_address=email_address,
            password=password,
        )
        self.save(account)
        return account.id

    def get_account_id_by_email(self, email_address: str) -> UUID:
        """Function used to get an account by email

        Args:
            email_address (str): email of the account to search

        Raises:
            AccountNotFoundError: If the account does not exist, raise
            an error

        Returns:
            UUID: unique identifier of the account
        """
        account_id = uuid5(NAMESPACE_URL, email_address)

        try:
            existing_account = self.repository.get(aggregate_id=account_id)
            if existing_account is None:
                raise AccountNotFoundError(email_address)
            return existing_account.id
        except AggregateNotFound:
            return account_id

    def authenticate(self, email_address: str, password: str) -> UUID:
        """Function used to make the authentication process

        Args:
            email_address (str): email of the account
            password (str): password of the account

        Raises:
            BadCredentials: If the credentials don't match, raise an error.

        Returns:
            UUID: unique identifier of the account
        """
        account_id = self.get_account_id_by_email(email_address)
        account = self.repository.get(account_id)
        if account.authenticate(email_address, password):
            return account_id
        raise BadCredentials(email_address)

    def get_account(self, account_id: UUID) -> Account:
        """Get accunt by its id

        Args:
            account_id (UUID): unique identifier of the account

        Returns:
            Account: Account instance
        """
        return self.repository.get(account_id)

    def deposit(self, account_id: UUID, amount: int) -> None:
        """Function used to make deposits in your account.


        Args:
            account_id (UUID): unique identifier of the account
            amount (int): Amount you want to deposit in the account
        """
        account = self.repository.get(account_id)
        account.credit(amount)
        self.save(account)

    def transfer(
        self,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: int,
    ) -> None:
        """Function used to transfer cash from your account to other

        Args:
            source_account_id (UUID): unique identifier of the source account
            destination_account_id (UUID): unique identifier of the destination
            account
            amount (int): Amount you want tansfer

        Raises:
            TransactionError: if the source and destination ids are the same,
            itraises an error.
        """
        source_account = self.repository.get(source_account_id)
        destination_account = self.repository.get(destination_account_id)

        if source_account_id == destination_account_id:
            raise TransactionError("Cannot transfer to the same account")

        source_account.debit(amount)
        destination_account.credit(amount)

        self.save(source_account, destination_account)

    def withdraw(self, account_id: UUID, amount: int) -> None:
        """Function used to make withdraws.

        Args:
            account_id (UUID): unique identifier of the account
            amount (int): amount you want to get
        """
        account = self.repository.get(account_id)
        account.debit(amount)
        self.save(account)
