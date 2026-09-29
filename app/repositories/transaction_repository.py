from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, account_id: int, transaction_type: str, amount: Decimal, status: str, reference_id: str) -> Transaction:
        transaction = Transaction(
            account_id=account_id,
            type=transaction_type,
            amount=Decimal(str(amount)),
            status=status,
            reference_id=reference_id,
        )
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def list_for_account(self, account_id: int):
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc())
            .all()
        )
