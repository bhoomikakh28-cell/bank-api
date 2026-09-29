from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class AccountSummaryResponse(BaseSchema):
    id: int
    user_id: int
    account_number: str
    balance: Decimal
    created_at: datetime


class AccountRead(BaseSchema):
    id: int
    user_id: int
    account_number: str
    balance: Decimal
    created_at: datetime


class DepositRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)


class WithdrawRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)


class TransferRequest(BaseModel):
    destination_account_number: str = Field(..., min_length=4, max_length=50)
    amount: Decimal = Field(..., gt=0)
