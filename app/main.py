from fastapi import FastAPI

from app.api.accounts import router as accounts_router
from app.api.auth import router as auth_router
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Basic Banking API",
    description="Backend-only banking API with authentication, account management, and transfers.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(accounts_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Basic Banking API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
