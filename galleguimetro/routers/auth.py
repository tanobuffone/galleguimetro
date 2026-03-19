from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_db
from ..models.schemas import UserCreate, UserLogin, TokenResponse, UserResponse, ApiResponse
from ..services.auth import register_user, login_user, get_current_user
from ..models.database import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await register_user(db, user_data)
    return ApiResponse(
        success=True,
        message="Usuario registrado exitosamente",
        data=result.model_dump(),
    )


@router.post("/login", response_model=ApiResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await login_user(db, credentials)
    return ApiResponse(
        success=True,
        message="Login exitoso",
        data=result.model_dump(),
    )


@router.get("/me", response_model=ApiResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    user_response = UserResponse.model_validate(current_user)
    return ApiResponse(
        success=True,
        message="Usuario actual",
        data=user_response.model_dump(),
    )
