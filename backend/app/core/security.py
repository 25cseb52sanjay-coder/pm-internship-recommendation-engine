from datetime import datetime, timedelta
from typing import Any, Union, Optional
import jwt
import bcrypt
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    # Ensure password is bytes and generate salt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

REVOKED_TOKENS = set()

def revoke_token(token: str):
    """Revoke JWT access token upon logout (Point 8 Specification)."""
    if token:
        REVOKED_TOKENS.add(token)

def is_token_revoked(token: str) -> bool:
    """Check if JWT token is revoked/logged out."""
    return token in REVOKED_TOKENS

def create_access_token(subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "iss": "PMIS_AUTH_SERVICE"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
