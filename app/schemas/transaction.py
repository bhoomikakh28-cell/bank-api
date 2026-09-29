from datetime import datetime
from decimal import Decimal

from app.schemas.base import BaseSchema


class TransactionRead(BaseSchema):
    id: int
    account_id: int
    type: str
    amount: Decimal
    status: str
    reference_id: str
    created_at: datetime
