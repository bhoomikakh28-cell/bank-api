import uuid
from decimal import Decimal

from app.core.exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidAmountError,
    SameAccountTransferError,
)
from app.models.transaction import Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository


class AccountService:
    def __init__(self, db):
        self.db = db
        self.account_repository = AccountRepository(db)
        self.transaction_repository = TransactionRepository(db)

    def get_account_for_user(self, user_id: int):
        account = self.account_repository.get_by_user_id(user_id)
        if not account:
            raise AccountNotFoundError("User account not found")
        return account

    def deposit(self, user_id: int, amount: Decimal):
        amount_value = Decimal(str(amount))
        if amount_value <= 0:
            raise InvalidAmountError("Amount must be greater than zero")

        account = self.get_account_for_user(user_id)
        account.balance = Decimal(str(account.balance)) + amount_value
        reference_id = str(uuid.uuid4())
        self.transaction_repository.create(account.id, "DEPOSIT", amount_value, "completed", reference_id)
        self.db.commit()
        self.db.refresh(account)
        return account

    def withdraw(self, user_id: int, amount: Decimal):
        amount_value = Decimal(str(amount))
        if amount_value <= 0:
            raise InvalidAmountError("Amount must be greater than zero")

        account = self.get_account_for_user(user_id)
        if Decimal(str(account.balance)) < amount_value:
            raise InsufficientFundsError("Insufficient funds for withdrawal")

        account.balance = Decimal(str(account.balance)) - amount_value
        reference_id = str(uuid.uuid4())
        self.transaction_repository.create(account.id, "WITHDRAW", amount_value, "completed", reference_id)
        self.db.commit()
        self.db.refresh(account)
        return account

    def transfer(self, user_id: int, destination_account_number: str, amount: Decimal):
        amount_value = Decimal(str(amount))
        if amount_value <= 0:
            raise InvalidAmountError("Amount must be greater than zero")

        source_account = self.get_account_for_user(user_id)
        if destination_account_number == source_account.account_number:
            raise SameAccountTransferError("Source and destination account cannot be the same")

        destination_account = self.account_repository.get_by_number(destination_account_number)
        if not destination_account:
            raise AccountNotFoundError("Destination account not found")

        if Decimal(str(source_account.balance)) < amount_value:
            raise InsufficientFundsError("Insufficient funds for transfer")

        reference_id = str(uuid.uuid4())
        try:
            source_account.balance = Decimal(str(source_account.balance)) - amount_value
            destination_account.balance = Decimal(str(destination_account.balance)) + amount_value

            self.transaction_repository.create(
                source_account.id,
                "TRANSFER_DEBIT",
                amount_value,
                "completed",
                reference_id,
            )
            self.transaction_repository.create(
                destination_account.id,
                "TRANSFER_CREDIT",
                amount_value,
                "completed",
                reference_id,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(source_account)
        self.db.refresh(destination_account)
        transfer_transactions = (
            self.db.query(Transaction)
            .filter(Transaction.reference_id == reference_id)
            .order_by(Transaction.created_at.asc())
            .all()
        )
        return source_account, destination_account, transfer_transactions

    def get_transactions(self, user_id: int):
        account = self.get_account_for_user(user_id)
        return self.transaction_repository.list_for_account(account.id)
