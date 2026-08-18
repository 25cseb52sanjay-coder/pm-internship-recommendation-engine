from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, UserRole, StudentProfile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

from app.db.models import User, UserRole, StudentProfile, RevokedToken

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Persistent DB Revocation Check (Point 8 Specification)
    rev_res = await db.execute(select(RevokedToken).where(RevokedToken.token == token))
    if rev_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or logged out",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_student(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StudentProfile:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Student access required")
        
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return current_user
