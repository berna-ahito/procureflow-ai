import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.core.security import create_access_token, verify_password
from app.db.base import get_db
from app.db.models import RefreshToken, User
from app.schemas.auth import AccessToken, LoginRequest, LogoutRequest, RefreshRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_TOKEN_EXPIRE_DAYS = 7


def _sha256_hex(value: str) -> str:
    """SHA-256 hex digest of a string — keeps payload under bcrypt's 72-byte limit."""
    return hashlib.sha256(value.encode()).hexdigest()


def _create_refresh_token(db: Session, user_id: int) -> str:
    raw_token = secrets.token_urlsafe(64)
    # SHA-256 first so the input to bcrypt is always exactly 64 hex chars (< 72 bytes).
    intermediate = _sha256_hex(raw_token)
    token_hash = bcrypt.hashpw(intermediate.encode(), bcrypt.gensalt()).decode()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()
    return raw_token


def _find_valid_refresh_token(db: Session, raw_token: str) -> RefreshToken:
    """Look up a non-revoked, non-expired RefreshToken matching raw_token.

    Raises HTTP 401 if not found or invalid.
    """
    # We must check all non-revoked, non-expired tokens because bcrypt is one-way.
    # Scan non-revoked, non-expired rows and verify each hash.
    now = datetime.now(timezone.utc)
    candidates = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.revoked == False,  # noqa: E712
            RefreshToken.expires_at > now,
        )
        .all()
    )
    intermediate = _sha256_hex(raw_token)
    for candidate in candidates:
        if bcrypt.checkpw(intermediate.encode(), candidate.token_hash.encode()):
            return candidate
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.is_active == True).first()  # noqa: E712
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"user_id": user.id, "role": user.role})
    refresh_token = _create_refresh_token(db, user.id)
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessToken)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    db_token = _find_valid_refresh_token(db, body.refresh_token)
    user = db.query(User).filter(User.id == db_token.user_id, User.is_active == True).first()  # noqa: E712
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"user_id": user.id, "role": user.role})
    return AccessToken(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    db_token = _find_valid_refresh_token(db, body.refresh_token)
    db_token.revoked = True
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
