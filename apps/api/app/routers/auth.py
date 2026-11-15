from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.deps import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest):
    # Skeleton implementation
    access_token = create_access_token(subject="user_placeholder")
    refresh_token = create_refresh_token(subject="user_placeholder", family_id="fam1", jti="jti1")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest):
    # Skeleton implementation
    access_token = create_access_token(subject="user_placeholder")
    refresh_token = create_refresh_token(subject="user_placeholder", family_id="fam1", jti="jti1")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user_id)):
    return UserResponse(
        id=user_id,
        email="user@example.com",
        display_name="Demo User",
        role="user",
        country="global",
        locale="en"
    )
