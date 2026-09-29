from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.account import Account


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Account | None:
        return self.db.query(Account).filter(Account.user_id == user_id).first()

    def get_by_number(self, account_number: str) -> Account | None:
        return self.db.query(Account).filter(Account.account_number == account_number).first()

    def create(self, user_id: int, account_number: str, balance: Decimal | str = "0.00") -> Account:
        account = Account(user_id=user_id, account_number=account_number, balance=Decimal(str(balance)))
        self.db.add(account)
        self.db.flush()
        return account

    def save(self, account: Account) -> Account:
        self.db.add(account)
        self.db.flush()
        return account
