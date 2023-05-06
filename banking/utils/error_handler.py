from functools import wraps

from werkzeug.exceptions import BadRequest
from eventsourcing.application import AggregateNotFound

from banking.utils.custom_exceptions import BadCredentials, TransactionError


def error_handler(func):
    """Decorator used to wrap all the logic inside a try/except block
    to not reapt try/except blocks in the code
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AggregateNotFound:
            return {"error": "Account not found."}, 404
        except BadCredentials as bad_credentials:
            return {"error": f"{str(bad_credentials)}"}, 401
        except TransactionError as transaction_error:
            return {"error": str(transaction_error)}, 400
        except Exception as exception:
            raise BadRequest(description=str(exception))

    return wrapper
