from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import create_access_token, verify_password
from ..database import get_db_cursor
from ..schemas import Token, UserLogin
from datetime import timedelta
from ..models import User

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login(form_data: UserLogin):
    with get_db_cursor() as cursor:
        user = User.get_by_email(cursor, form_data.email)
        if not user or not verify_password(form_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
