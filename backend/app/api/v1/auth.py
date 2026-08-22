from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.db.database import get_db
from app.db.models import User, StudentProfile, UserRole
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import Token, LoginRequest, RegisterRequest, GoogleAuthRequest, UserOut
from app.api.v1.deps import get_current_user
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    clean_email = data.email.strip().lower()
    res = await db.execute(select(User).where(func.lower(func.trim(User.email)) == clean_email))
    existing_user = res.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(data.password)
    user = User(
        email=clean_email,
        password_hash=hashed_pw,
        full_name=data.full_name,
        provider="LOCAL",
        role=data.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    if user.role == UserRole.STUDENT:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
        await db.commit()

    token = create_access_token(subject=user.id, role=user.role)

    response.set_cookie(
        key="pm_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7
    )

    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        provider=user.provider
    )

@router.post("/login", response_model=Token)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    if not data.email or not data.email.strip() or not data.password or not data.password.strip():
        raise HTTPException(status_code=400, detail="Invalid email or password")

    clean_email = data.email.strip().lower()
    res = await db.execute(select(User).where(func.lower(func.trim(User.email)) == clean_email))
    user = res.scalar_one_or_none()

    req_role = (data.requested_role or "").upper()

    # 1. User Not Found Check
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account Not Found: No registered account found for '{clean_email}'."
        )

    # 2. Portal Role Alignment Verification
    if req_role == "ADMIN" and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: This account is registered as a Student Account and does not have Admin Portal privileges."
        )

    if req_role == "STUDENT" and user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin Account Detected: This email belongs to an Admin Portal account. Please select the 'Admin Portal' tab to sign in."
        )

    # 3. Strict Password Verification Check
    if not verify_password(data.password.strip(), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Password: The password entered is incorrect for '{clean_email}'."
        )

    token = create_access_token(subject=user.id, role=user.role)

    response.set_cookie(
        key="pm_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7
    )

    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        avatar_url=user.avatar_url,
        provider=user.provider,
        preferred_locale=getattr(user, "preferred_locale", "en")
    )

@router.post("/google", response_model=Token)
async def google_login(
    data: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Two-Stage Google Authentication & SQL Authorization:
    STAGE 1: Google OAuth 2.0 verifies token signature, issuer, audience, & expiration server-side.
    STAGE 2: SQL Database checks whether verified Google email belongs to a registered candidate.
    """
    # --- STAGE 1: GOOGLE AUTHENTICATION ---
    try:
        raw_cid = settings.GOOGLE_CLIENT_ID.strip() if settings.GOOGLE_CLIENT_ID else ""
        client_id = raw_cid if raw_cid and raw_cid not in ["YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com", "104928172938-samplegoogleclientid.apps.googleusercontent.com"] else None

        id_info = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            audience=client_id
        )

        if id_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token issuer")

        google_sub = id_info.get("sub")
        raw_email = id_info.get("email")
        picture = id_info.get("picture")

        if not google_sub or not raw_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token missing identity claims")

        clean_google_email = raw_email.strip().lower()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Google token verification failed: {str(e)}")

    # --- STAGE 2: SQL DATABASE AUTHORIZATION ---
    # Query SQL database using verified Google email
    res = await db.execute(select(User).where(func.lower(func.trim(User.email)) == clean_google_email))
    user = res.scalar_one_or_none()

    # Automatically provision account for Google Cloud verified legitimate users
    if not user:
        assigned_role = UserRole.ADMIN if clean_google_email == "adminpminternship@gmail.com" else UserRole.STUDENT
        user = User(
            email=clean_google_email,
            password_hash="GOOGLE_OAUTH_USER",
            full_name=id_info.get("name", clean_google_email.split("@")[0].title()),
            role=assigned_role,
            provider="GOOGLE",
            google_subject_id=google_sub,
            avatar_url=picture
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Link google_subject_id and avatar if missing
    if not user.google_subject_id or not user.avatar_url:
        user.google_subject_id = google_sub
        if picture and not user.avatar_url:
            user.avatar_url = picture
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Ensure profile exists for candidate
    if user.role == UserRole.STUDENT:
        prof_res = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
        if not prof_res.scalar_one_or_none():
            profile = StudentProfile(user_id=user.id)
            db.add(profile)
            await db.commit()

    # Create application JWT session
    token = create_access_token(subject=user.id, role=user.role)

    response.set_cookie(
        key="pm_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7
    )

    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        avatar_url=user.avatar_url,
        provider=user.provider
    )

from app.db.models import RevokedToken
from app.api.v1.deps import oauth2_scheme

@router.post("/logout")
async def logout(
    response: Response,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    if token:
        try:
            rev = RevokedToken(token=token)
            db.add(rev)
            await db.commit()
        except Exception:
            pass
    response.delete_cookie(key="pm_session", path="/")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
