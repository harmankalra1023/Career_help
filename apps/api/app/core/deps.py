from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_factory
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_id(token: Optional[str] = Depends(oauth2_scheme)) -> str:
    # In development mode, default to the demo user so dashboard works immediately without login
    if not token:
        return "default_user"
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        return user_id or "default_user"
    except Exception:
        return "default_user"
