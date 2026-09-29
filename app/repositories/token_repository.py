from datetime import datetime

from sqlalchemy.orm import Session

from app.models.blacklisted_token import BlacklistedToken


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_blacklisted(self, jti: str) -> bool:
        return self.db.query(BlacklistedToken).filter(BlacklistedToken.jti == jti).first() is not None

    def blacklist(self, jti: str, expires_at: datetime) -> BlacklistedToken:
        token = BlacklistedToken(jti=jti, expires_at=expires_at)
        self.db.add(token)
        self.db.flush()
        return token
