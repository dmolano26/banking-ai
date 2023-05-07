from uuid import UUID


class TransactionError(Exception):
    """Exception used when any transfer fails"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AccountClosedError(Exception):
    """Exception used to validate if the account is still open"""

    def __init__(self, account_id: UUID) -> None:
        self.account_id = account_id
        super().__init__(f"Account with ID {account_id} is closed")


class InsufficientFundsError(Exception):
    """Exception used when the account does not have sufficient founds"""

    def __init__(self, current_balance: int, withdrawal_amount: int) -> None:
        self.current_balance = current_balance
        self.withdrawal_amount = withdrawal_amount
        super().__init__(
            f"Insufficient funds: Current balance is {current_balance}, "
            f"but the requested withdrawal amount is {withdrawal_amount}"
        )


class BadCredentials(Exception):
    """Exception used when the login fails"""

    def __init__(self, email_address: str) -> None:
        self.email_address = email_address
        super().__init__(f"Bad credentials for email address: {email_address}")


class AccountNotFoundError(Exception):
    """Exception used when the account is not in the system"""

    def __init__(self, email_address: str) -> None:
        self.email_address = email_address
        super().__init__(
            f"Account not found for email address: {email_address}"
        )
