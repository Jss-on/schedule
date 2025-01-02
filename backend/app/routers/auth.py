from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import create_access_token, verify_password, get_password_hash, get_current_user
from ..database import get_db_cursor
from ..schemas import Token, UserLogin, CoordinatorCreate
from datetime import timedelta
from ..models import User
from typing import List

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login(form_data: UserLogin):
    with get_db_cursor() as cursor:
        user = User.get_by_email(cursor, form_data.email)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/coordinators", response_model=dict)
async def create_coordinator(
    coordinator: CoordinatorCreate,
    current_user: dict = Depends(get_current_user)
):
    # Check if the current user is an admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create coordinator accounts"
        )
    
    with get_db_cursor() as cursor:
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (coordinator.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new coordinator
        hashed_password = get_password_hash(coordinator.password)
        new_coordinator = User.create(
            cursor=cursor,
            email=coordinator.email,
            hashed_password=hashed_password,
            full_name=coordinator.full_name,
            role="coordinator"  # Explicitly set role as coordinator
        )
        
        return {"message": "Coordinator created successfully", "email": new_coordinator.email}

@router.get("/users/coordinators", response_model=List[dict])
async def list_coordinators(current_user: dict = Depends(get_current_user)):
    # Check if the current user is an admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view coordinator list"
        )
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, email, full_name, created_at, updated_at
            FROM users
            WHERE role = 'coordinator'
            ORDER BY created_at DESC
        """)
        coordinators = cursor.fetchall()
        return coordinators
