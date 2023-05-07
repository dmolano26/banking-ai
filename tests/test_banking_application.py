# coding=utf-8

import typing
from uuid import UUID

import pytest
from werkzeug.exceptions import BadRequest
from eventsourcing.application import AggregateNotFound


from banking.applicationmodel import Bank, AccountNotFoundError
from banking.utils.error_handler import error_handler
from banking.utils.custom_exceptions import (
    AccountClosedError,
    InsufficientFundsError,
    BadCredentials,
    TransactionError,
)


def assertEqual(x: typing.Any, y: typing.Any) -> None:
    assert x == y


def _create_alice_with_200(app: Bank) -> UUID:
    # Create alice.
    alice = app.open_account(
        full_name="Alice",
        email_address="alice@example.com",
        password="alice",
    )

    # Check balance of alice.
    assertEqual(app.get_balance(alice), 0)

    # Deposit funds in alice.
    app.deposit_funds(
        account_id=alice,
        amount=10000,
    )

    # Deposit funds in alice.
    app.deposit_funds(
        account_id=alice,
        amount=10000,
    )

    return alice


def _create_bob(app: Bank) -> UUID:
    # Create bob.
    bob = app.open_account(
        full_name="Bob",
        email_address="bob@example.com",
        password="bob",
    )

    # Check balance of alice.
    assertEqual(app.get_balance(bob), 0)

    # Deposit funds in bob.
    app.deposit_funds(
        account_id=bob,
        amount=100,
    )

    # Deposit funds in bob.
    app.deposit_funds(
        account_id=bob,
        amount=100,
    )

    return bob


def _create_sue(app: Bank) -> UUID:
    # Create sue.
    sue = app.open_account(
        full_name="Sue",
        email_address="sue@example.com",
        password="sue",
    )

    # Check balance of sue.
    assertEqual(app.get_balance(sue), 0)

    # Deposit funds in sue.
    app.deposit_funds(
        account_id=sue,
        amount=100,
    )

    return sue


def test_account_does_not_exist() -> None:
    app = Bank()
    alice = app.get_account_id_by_email("alice@example.com")
    # Check account not found error.
    with pytest.raises(AccountNotFoundError):
        app.get_balance(alice)


def test_deposit() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)
    bob = _create_bob(app)

    # Check balance of alice.
    assertEqual(app.get_balance(alice), 20000)

    # Check balance of alice.
    assertEqual(app.get_balance(bob), 200)


def test_withdraw() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)

    # Withdraw funds from alice.
    app.withdraw_funds(
        account_id=alice,
        amount=5000,
    )

    # Check balance of alice.
    assertEqual(app.get_balance(alice), 15000)


def test_insufficient() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)

    # Fail to withdraw funds from alice- insufficient funds.
    with pytest.raises(InsufficientFundsError):
        app.withdraw_funds(
            account_id=alice,
            amount=25000,
        )

    # Check balance of alice - should be unchanged.
    assertEqual(app.get_balance(alice), 20000)


def test_transfer() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)
    bob = _create_bob(app)
    sue = _create_sue(app)

    # Transfer funds from alice to bob.
    app.transfer_funds(
        source_account_id=alice,
        destination_account_id=bob,
        amount=5000,
    )

    # Transfer funds from bob to sue.
    app.transfer_funds(
        source_account_id=bob,
        destination_account_id=sue,
        amount=100,
    )

    # Check balances.
    assertEqual(app.get_balance(alice), 15000)
    assertEqual(app.get_balance(bob), 5100)
    assertEqual(app.get_balance(sue), 200)

    # Fail to transfer funds - insufficient funds.
    with pytest.raises(InsufficientFundsError):
        app.transfer_funds(
            source_account_id=alice,
            destination_account_id=bob,
            amount=100000,
        )

    # Check balances - should be unchanged.
    assertEqual(app.get_balance(alice), 15000)
    assertEqual(app.get_balance(bob), 5100)
    assertEqual(app.get_balance(sue), 200)

    # Fail to transfer funds - transfer to the same account.
    with pytest.raises(TransactionError):
        app.transfer_funds(
            source_account_id=alice,
            destination_account_id=alice,
            amount=100000,
        )


def test_closed() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)
    bob = _create_bob(app)

    # Close alice .
    app.close_account(alice)

    # Fail to transfer funds - alice  is closed.
    with pytest.raises(AccountClosedError):
        app.transfer_funds(
            source_account_id=alice,
            destination_account_id=bob,
            amount=5000,
        )

    # Fail to withdraw funds - alice is closed.
    with pytest.raises(AccountClosedError):
        app.withdraw_funds(
            account_id=alice,
            amount=100,
        )

    # Fail to deposit funds - alice is closed.
    with pytest.raises(AccountClosedError):
        app.deposit_funds(
            account_id=alice,
            amount=100000,
        )

    # Fail to set overdraft limit on alice - account is closed.
    with pytest.raises(AccountClosedError):
        app.set_overdraft_limit(
            account_id=alice,
            amount=50000,
        )

    # Check balances - should be unchanged.
    assertEqual(app.get_balance(alice), 20000)
    assertEqual(app.get_balance(bob), 200)

    # Check overdraft limits - should be unchanged.
    assertEqual(
        app.get_overdraft_limit(alice),
        0,
    )
    assertEqual(
        app.get_overdraft_limit(bob),
        0,
    )


def test_debit() -> None:
    app = Bank()
    alice = _create_alice_with_200(app)
    account = app.get_account(alice)
    with pytest.raises(ValueError):
        account.debit(-1)


def test_overdraft() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)
    bob = _create_bob(app)

    # Check overdraft limit of alice.
    assertEqual(
        app.get_overdraft_limit(alice),
        0,
    )

    # Set overdraft limit on bob.
    app.set_overdraft_limit(
        account_id=bob,
        amount=50000,
    )

    # Can't set negative overdraft limit.
    with pytest.raises(AssertionError):
        app.set_overdraft_limit(
            account_id=bob,
            amount=-50000,
        )

    # Check overdraft limit of bob.
    assertEqual(
        app.get_overdraft_limit(bob),
        50000,
    )

    # Withdraw funds from bob.
    app.withdraw_funds(
        account_id=bob,
        amount=50200,
    )

    # Check balance of bob - should be overdrawn.
    assertEqual(
        app.get_balance(bob),
        -50000,
    )

    # Fail to withdraw funds from bob - insufficient funds.
    with pytest.raises(InsufficientFundsError):
        app.withdraw_funds(
            account_id=bob,
            amount=100,
        )


def test_password() -> None:
    app = Bank()

    alice = _create_alice_with_200(app)

    app.validate_password(alice, "alice")
    app.change_password(alice, "alice", "alice2")
    app.validate_password(alice, "alice2")
    with pytest.raises(BadCredentials):
        app.validate_password(alice, "alice")


def test_error_handler_decorator():
    @error_handler
    def raise_aggregate_not_found():
        raise AggregateNotFound()

    @error_handler
    def raise_bad_credentials():
        raise BadCredentials("Bad credentials.")

    @error_handler
    def raise_transaction_error():
        raise TransactionError("Transaction error.")

    @error_handler
    def raise_generic_exception():
        raise Exception("Generic exception.")

    # Test AggregateNotFound handling
    response, status_code = raise_aggregate_not_found()
    assert response == {"error": "Account not found."}
    assert status_code == 404

    # Test BadCredentials handling
    response, status_code = raise_bad_credentials()
    assert response == {
        "error": "Bad credentials for email address: Bad credentials."
    }
    assert status_code == 401

    # Test TransactionError handling
    response, status_code = raise_transaction_error()
    assert response == {"error": "Transaction error."}
    assert status_code == 400

    # Test generic Exception handling
    with pytest.raises(BadRequest):
        raise_generic_exception()
