import uuid
from datetime import datetime

from app.core.exceptions import DuplicateEmailError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.account_repository import AccountRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db):
        self.db = db
        self.user_repository = UserRepository(db)
        self.account_repository = AccountRepository(db)
        self.token_repository = TokenRepository(db)

    def register(self, name: str, email: str, password: str):
        normalized_email = email.lower().strip()
        if self.user_repository.get_by_email(normalized_email):
            raise DuplicateEmailError("Email already registered")

        hashed_password = hash_password(password)
        user = self.user_repository.create(name.strip(), normalized_email, hashed_password)
        account_number = self._generate_unique_account_number()
        account = self.account_repository.create(user.id, account_number, "0.00")
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(account)

        token = create_access_token(str(user.id), str(uuid.uuid4()))
        return user, account, token

    def login(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        token = create_access_token(str(user.id), str(uuid.uuid4()))
        return token

    def logout(self, jti: str, expires_at: datetime) -> None:
        self.token_repository.blacklist(jti, expires_at)
        self.db.commit()

    def _generate_unique_account_number(self) -> str:
        while True:
            candidate = f"ACC-{uuid.uuid4().hex[:10].upper()}"
            if not self.account_repository.get_by_number(candidate):
                return candidate
