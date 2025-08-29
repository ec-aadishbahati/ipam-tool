from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from app.db.session import get_db
from app.db.models import User
from app.schemas.user import UserCreate, UserLogin, UserOut, PasswordChange
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.email == payload.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=payload.email, 
        hashed_password=get_password_hash(payload.password), 
        is_admin=False,
        must_change_password=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    email_to_check = payload.email
    if payload.email == "admin":
        email_to_check = settings.ADMIN_EMAIL
    
    q = await db.execute(select(User).where(User.email == email_to_check))
    user = q.scalar_one_or_none()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    
    if user.must_change_password:
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "must_change_password": True,
            "message": "Password change required on first login"
        }
    
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/change-password")
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    current_user.hashed_password = get_password_hash(payload.new_password)
    current_user.must_change_password = False
    current_user.password_changed_at = datetime.utcnow()
    
    await db.commit()
    return {"message": "Password changed successfully"}


@router.post("/refresh")
async def refresh(payload: dict, db: AsyncSession = Depends(get_db)):
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required")
    try:
        jwt_payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
        sub = jwt_payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        uid = int(sub)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    q = await db.execute(select(User).where(User.id == uid))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
