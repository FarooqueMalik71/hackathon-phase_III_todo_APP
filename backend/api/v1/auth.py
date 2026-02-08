from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
from core.security import create_access_token
from models.user import User, UserCreate, UserRead
from db.session import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext

router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserRead


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    token: str
    user: UserRead


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(password_bytes, hashed_password)


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)



@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    session: AsyncSession = Depends(get_async_session)
):
    # Find user by email
    statement = select(User).where(User.email == login_request.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

    return LoginResponse(token=access_token, user=UserRead.model_validate(user))


@router.post("/register", response_model=RegisterResponse)
async def register(
    register_request: RegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    # Check if user already exists
    statement = select(User).where(User.email == register_request.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Hash the password
    hashed_password = hash_password(register_request.password)

    # Create new user
    user = User(
        id=uuid.uuid4(),
        name=register_request.name,
        email=register_request.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

    return RegisterResponse(token=access_token, user=UserRead.model_validate(user))