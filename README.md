# Basic Banking API

This project is a backend-only FastAPI application for a simple banking system. It supports user registration, JWT authentication, account management, deposits, withdrawals, transfers, and transaction history using SQLite and SQLAlchemy.

## 1. Project Overview

The Basic Banking API is designed to be beginner-friendly and easy to follow. It focuses on the core banking flows expected in a student assessment:

- user registration and login
- JWT-based authentication
- account creation on registration
- deposit and withdrawal logic
- transfer between accounts
- transaction history for the authenticated user
- token logout / blacklisting
- database-backed persistence with SQLite

## 2. Features

- User registration with unique email validation
- Password hashing with bcrypt
- JWT access tokens with expiration
- Account creation automatically on registration
- Deposit, withdrawal, and transfer operations
- Business validation to prevent negative balances and invalid transfers
- Transaction history with newest-first ordering
- Logout that blacklists the JWT token
- Swagger documentation via FastAPI

## 3. Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite
- Pydantic v2
- PyJWT
- bcrypt
- pytest
- httpx
- python-dotenv / pydantic-settings

## 4. Project Structure

```text
bank-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   ├── auth.py
│   │   └── accounts.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   └── blacklisted_token.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── auth.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── account_service.py
│   └── repositories/
│       ├── __init__.py
│       ├── user_repository.py
│       ├── account_repository.py
│       ├── transaction_repository.py
│       └── token_repository.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_accounts.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── bank.db
```

## 5. Prerequisites

- Python 3.11 or newer
- pip
- local environment allowed to create a virtual environment

## 6. Installation

```bash
cd "/Users/bhoomi/# PROJECT- BASIC BANKING API — BACKEND /bank-api"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 7. Environment Variables

Create a local `.env` file from `.env.example` and update the secret value before running the API.

```env
DATABASE_URL=sqlite:///./bank.db
SECRET_KEY=change-this-in-development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 8. Database

The project uses SQLite and the default database file is `bank.db`.

Tables are created automatically when the app starts:

- users
- accounts
- transactions
- blacklisted_tokens

## 9. How to Run

```bash
cd "/Users/bhoomi/# PROJECT- BASIC BANKING API — BACKEND /bank-api"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 10. API Endpoints

### Authentication

- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout

### Accounts

- GET /api/accounts/me
- POST /api/accounts/deposit
- POST /api/accounts/withdraw
- POST /api/accounts/transfer
- GET /api/accounts/transactions

## 11. Authentication

Authentication uses JWT bearer tokens.

Use the token in the Authorization header:

```http
Authorization: Bearer <token>
```

The token contains:

- a subject (user ID)
- a unique JTI
- an expiration timestamp

## 12. Logout / Token Blacklisting

When a user logs out, the current JWT is stored in the `blacklisted_tokens` table. Protected requests reject any blacklisted token.

## 13. Database Design

- `User` has many `Account` records
- each user has a single main account in this design
- `Account` has many `Transaction` records
- `Transaction` stores the transaction type, amount, status, and reference ID
- `BlacklistedToken` stores revoked JWT identifiers with expiration times

## 14. Design Decisions

- Money is handled as Decimal values, not floats
- Business rules are kept in the service layer
- Database access is handled in repositories
- Routes remain focused on HTTP concerns
- Transactions are wrapped for safe transfer operations

## 15. Testing

```bash
cd "/Users/bhoomi/# PROJECT- BASIC BANKING API — BACKEND /bank-api"
source venv/bin/activate
pytest
```

## 16. Example Requests

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "password": "strongpass123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "strongpass123"
  }'
```

### Get account

```bash
curl http://localhost:8000/api/accounts/me \
  -H "Authorization: Bearer <token>"
```

### Deposit

```bash
curl -X POST http://localhost:8000/api/accounts/deposit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": "50.00"}'
```

### Withdraw

```bash
curl -X POST http://localhost:8000/api/accounts/withdraw \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": "10.00"}'
```

### Transfer

```bash
curl -X POST http://localhost:8000/api/accounts/transfer \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "destination_account_number": "ACC-123ABC",
    "amount": "25.00"
  }'
```

## 17. Swagger / API Documentation

FastAPI provides Swagger UI at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## 18. Limitations / Future Improvements

- This project intentionally keeps the scope focused on the basic banking API assessment.
- It uses one SQLite database file for a local development environment.
- It does not include a frontend or payment gateway integration.
- Additional features such as multi-account support, admin roles, or scheduled transfers could be added later.
