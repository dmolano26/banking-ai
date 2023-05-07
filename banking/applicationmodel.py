# coding=utf-8

from uuid import NAMESPACE_URL, UUID, uuid5
from hashlib import sha512

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

    def close_account(self, account_id: UUID) -> None:
        """Function used to close an existing account

        Args:
            account_id (UUID)
        """
        account = self.repository.get(account_id)
        account.close_account()
        self.save(account)

    def get_account_id_by_email(self, email_address: str) -> UUID:
        """Function used to get an account by email

        Args:
            email_address (str)

        Raises:
            AccountNotFoundError

        Returns:
            UUID
        """
        account_id = uuid5(NAMESPACE_URL, email_address)

        try:
            existing_account = self.repository.get(account_id)
            return existing_account.id
        except AggregateNotFound:
            return account_id

    def authenticate(self, email_address: str, password: str) -> UUID:
        """Function used to make the authentication process

        Args:
            email_address (str)
            password (str)

        Raises:
            BadCredentials

        Returns:
            UUID
        """
        account_id = self.get_account_id_by_email(email_address)
        account = self.repository.get(account_id)
        if account.authenticate(email_address, password):
            return account_id
        raise BadCredentials(email_address)

    def validate_password(self, account_id: UUID, password: str) -> bool:
        """Validate if the incoming password matchs with the account's password

        Args:
            account_id (UUID)
            password (str)

        Raises:
            BadCredentials

        Returns:
            bool
        """
        account = self.repository.get(account_id)
        hashed_password = sha512(password.encode()).hexdigest()
        if not hashed_password.__eq__(account.hashed_password):
            raise BadCredentials(account.email_address)
        return True

    def change_password(
        self, account_id: UUID, current_password: str, new_password: str
    ) -> None:
        """Function used to change the password for the account

        Args:
            account_id (UUID)
            current_password (str)
            new_password (str)
        """
        if self.validate_password(account_id, current_password):
            account = self.repository.get(account_id)
            account.change_password(new_password)
            self.save(account)

    def get_account(self, account_id: UUID) -> Account:
        """Get accunt by its id

        Args:
            account_id (UUID)

        Returns:
            Account
        """
        return self.repository.get(account_id)

    def get_balance(self, account_id: UUID) -> int:
        """Get balance by account ID

        Args:
            account_id (UUID)

        Returns:
            int
        """
        try:
            account = self.repository.get(account_id)
        except AggregateNotFound:
            raise AccountNotFoundError(
                f"Account with ID {account_id} not found"
            )

        return account.balance

    def deposit_funds(self, account_id: UUID, amount: int) -> None:
        """Function used to make deposits in your account.

        Args:
            account_id (UUID)
            amount (int)
        """
        account = self.repository.get(account_id)
        account.check_if_closed()
        account.credit(amount)
        self.save(account)

    def transfer_funds(
        self,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: int,
    ) -> None:
        """Function used to transfer cash from your account to other

        Args:
            source_account_id (UUID)
            destination_account_id (UUID)
            amount (int)

        Raises:
            TransactionError
        """
        source_account = self.repository.get(source_account_id)
        destination_account = self.repository.get(destination_account_id)

        if source_account_id == destination_account_id:
            raise TransactionError("Cannot transfer to the same account")

        source_account.check_if_closed()
        destination_account.check_if_closed()

        source_account.debit(amount)
        destination_account.credit(amount)

        self.save(source_account, destination_account)

    def withdraw_funds(self, account_id: UUID, amount: int) -> None:
        """Function used to make withdraws.

        Args:
            account_id (UUID)
            amount (int)
        """
        account = self.repository.get(account_id)
        account.check_if_closed()
        account.debit(amount)
        self.save(account)

    def get_overdraft_limit(self, account_id: UUID) -> int:
        """Function used to get the current overdraft limit of the account

        Args:
            account_id (UUID)

        Returns:
            int
        """
        account = self.repository.get(account_id)
        return account.get_overdraft_limit()

    def set_overdraft_limit(self, account_id: UUID, amount: int) -> None:
        """Function used to set the new overdraft limit to the account

        Args:
            account_id (UUID)
            amount (int)
        """
        account = self.repository.get(account_id)
        account.check_if_closed()
        account.set_overdraft_limit(amount)
        self.save(account)
