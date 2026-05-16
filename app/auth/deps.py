"""FastAPI auth dependencies."""
from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwe import COOKIE_NAME, decode
from app.db.session import get_session
from app.models.user import User


async def current_user(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> User:
    """Resolve the logged-in User from the encrypted session cookie or raise 401."""
    token = request.cookies.get(COOKIE_NAME)
    claims = decode(token) if token else None
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user_id = UUID(claims["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
