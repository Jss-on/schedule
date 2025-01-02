from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    student_name: str
    student_email: EmailStr
    student_phone: str
    special_requirements: Optional[str] = None
    instructor_id: int
    vehicle_id: int

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    student_name: Optional[str] = None
    student_email: Optional[EmailStr] = None
    student_phone: Optional[str] = None
    special_requirements: Optional[str] = None
    instructor_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    status: Optional[str] = None

class Appointment(AppointmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class InstructorBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    specialization: Optional[str] = None

class InstructorCreate(InstructorBase):
    pass

class InstructorResponse(InstructorBase):
    id: int
    created_at: datetime
    updated_at: datetime
