from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidAmountError,
    SameAccountTransferError,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.account import AccountRead, DepositRequest, TransferRequest, WithdrawRequest
from app.schemas.transaction import TransactionRead
from app.services.account_service import AccountService

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.get("/me", response_model=AccountRead)
def get_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        account = AccountService(db).get_account_for_user(current_user.id)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return account


@router.post("/deposit", response_model=AccountRead)
def deposit_to_account(
    payload: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        account = AccountService(db).deposit(current_user.id, payload.amount)
    except InvalidAmountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return account


@router.post("/withdraw", response_model=AccountRead)
def withdraw_from_account(
    payload: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        account = AccountService(db).withdraw(current_user.id, payload.amount)
    except InvalidAmountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InsufficientFundsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return account


@router.post("/transfer")
def transfer_funds(
    payload: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        source_account, destination_account, transactions = AccountService(db).transfer(
            current_user.id,
            payload.destination_account_number,
            payload.amount,
        )
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidAmountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SameAccountTransferError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InsufficientFundsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "message": "Transfer completed successfully",
        "source_account": {
            "id": source_account.id,
            "user_id": source_account.user_id,
            "account_number": source_account.account_number,
            "balance": str(source_account.balance),
            "created_at": source_account.created_at,
        },
        "destination_account": {
            "id": destination_account.id,
            "user_id": destination_account.user_id,
            "account_number": destination_account.account_number,
            "balance": str(destination_account.balance),
            "created_at": destination_account.created_at,
        },
        "transactions": [
            {
                "id": item.id,
                "account_id": item.account_id,
                "type": item.type,
                "amount": str(item.amount),
                "status": item.status,
                "reference_id": item.reference_id,
                "created_at": item.created_at,
            }
            for item in transactions
        ],
    }


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AccountService(db).get_transactions(current_user.id)
