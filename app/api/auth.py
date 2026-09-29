from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, oauth2_scheme
from app.core.exceptions import DuplicateEmailError, InvalidCredentialsError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.schemas.auth import RegisterResponse, TokenResponse, UserLoginRequest, UserPublicResponse, UserRegistrationRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegistrationRequest, db: Session = Depends(get_db)):
    try:
        user, account, token = AuthService(db).register(payload.name, payload.email, payload.password)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
        },
        "account": {
            "id": account.id,
            "user_id": account.user_id,
            "account_number": account.account_number,
            "balance": account.balance,
            "created_at": account.created_at,
        },
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        token = AuthService(db).login(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
):
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    AuthService(db).logout(payload["jti"], expires_at)
    return {"message": "Logged out successfully"}
