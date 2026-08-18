from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from app.db.database import get_db
from app.db.models import User
from app.api.v1.deps import get_current_user

router = APIRouter()

class UserPreferenceUpdate(BaseModel):
    preferred_locale: str = Field(..., description="Locale code (e.g. en, hi, ta, te, ar, ur, etc.)")

class UserPreferenceOut(BaseModel):
    preferred_locale: str

@router.get("/preferences", response_model=UserPreferenceOut)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns preferred language locale for the authenticated user."""
    return UserPreferenceOut(preferred_locale=current_user.preferred_locale or "en")

@router.patch("/preferences", response_model=UserPreferenceOut)
async def update_user_preferences(
    data: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates preferred language locale for the authenticated user."""
    valid_locales = {
        "en", "hi", "te", "ta", "kn", "ml", "ur", "pa", "sd", "mr",
        "gu", "bn", "or", "fr", "zh", "ar", "pt", "de", "ja", "ko",
        "it", "tr", "ms", "ne", "sw"
    }
    
    clean_locale = data.preferred_locale.strip().lower()
    if clean_locale not in valid_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported locale '{clean_locale}'. Must be one of {sorted(list(valid_locales))}"
        )

    current_user.preferred_locale = clean_locale
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return UserPreferenceOut(preferred_locale=current_user.preferred_locale)
