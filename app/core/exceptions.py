class BankingAPIException(Exception):
    """Base exception for banking API domain errors."""


class DuplicateEmailError(BankingAPIException):
    pass


class InvalidCredentialsError(BankingAPIException):
    pass


class AccountNotFoundError(BankingAPIException):
    pass

class UserNotFoundError(BankingAPIException):
    pass


class InsufficientFundsError(BankingAPIException):
    pass


class InvalidAmountError(BankingAPIException):
    pass


class SameAccountTransferError(BankingAPIException):
    pass
