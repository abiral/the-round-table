"""Auth endpoints: /login, /logout, /me."""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.auth.jwe import COOKIE_NAME, encode
from app.auth.schemas import LoginRequest, UserOut
from app.db.session import get_session
from app.models.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _cookie_kwargs() -> dict:
    secure = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "lax",
        "path": "/",
    }


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=str(user.id),
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
    )


@router.post("/login", response_model=UserOut)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_session),
):
    """Verify credentials using pgcrypto's crypt() and set the JWE cookie."""
    row = (
        await db.execute(
            text(
                """
                SELECT id, firstname, lastname, email
                  FROM users
                 WHERE lower(email) = lower(:email)
                   AND password = crypt(:password, password)
                """
            ),
            {"email": payload.email, "password": payload.password},
        )
    ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = encode(str(row["id"]))
    response.set_cookie(key=COOKIE_NAME, value=token, **_cookie_kwargs())

    return UserOut(
        id=str(row["id"]),
        firstname=row["firstname"],
        lastname=row["lastname"],
        email=row["email"],
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)):
    return _user_out(user)
