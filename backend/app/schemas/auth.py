from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    provider: Optional[str] = "LOCAL"
    preferred_locale: Optional[str] = "en"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    requested_role: Optional[str] = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.STUDENT
    preferred_locale: Optional[str] = "en"

class GoogleAuthRequest(BaseModel):
    credential: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    provider: Optional[str] = "LOCAL"
    avatar_url: Optional[str] = None
    preferred_locale: Optional[str] = "en"

    class Config:
        from_attributes = True
