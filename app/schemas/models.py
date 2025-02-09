from datetime import datetime, date, time
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field, validator
import re
import os

# Get validation patterns from environment variables
PHONE_NUMBER_PATTERN = os.getenv('PHONE_NUMBER_PATTERN', r'^\+?1?\d{9,15}$')
DATE_FORMAT_PATTERN = os.getenv('DATE_FORMAT_PATTERN', r'^\d{4}-\d{2}-\d{2}$')

def validate_phone(v: str) -> str:
    if not re.match(PHONE_NUMBER_PATTERN, v):
        raise ValueError('Invalid phone number')
    return v

class TimeSlot(BaseModel):
    start: time
    end: time

    @validator('start', 'end')
    def convert_str_to_time(cls, v):
        if isinstance(v, str):
            try:
                # Accept both HH:MM and H:MM formats
                return datetime.strptime(v, '%H:%M').time()
            except ValueError:
                try:
                    return datetime.strptime(v, '%-I:%M %p').time()
                except ValueError:
                    raise ValueError('Time must be in HH:MM (24hr) or H:MM AM/PM format')
        return v

    @validator('end')
    def validate_end_time(cls, v, values):
        if 'start' in values and v <= values['start']:
            raise ValueError('End time must be after start time')
        return v

class DaySchedule(BaseModel):
    monday: Optional[List[TimeSlot]] = []
    tuesday: Optional[List[TimeSlot]] = []
    wednesday: Optional[List[TimeSlot]] = []
    thursday: Optional[List[TimeSlot]] = []
    friday: Optional[List[TimeSlot]] = []
    saturday: Optional[List[TimeSlot]] = []
    sunday: Optional[List[TimeSlot]] = []

class InstructorUnavailabilityBase(BaseModel):
    start_time: datetime = Field(..., description="Start time in YYYY-MM-DD HH:MM format")
    end_time: datetime = Field(..., description="End time in YYYY-MM-DD HH:MM format")
    reason: Optional[str] = None

    @validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        if not isinstance(v, datetime):
            try:
                # Try parsing with the expected format
                return datetime.strptime(v, '%Y-%m-%d %H:%M')
            except ValueError:
                raise ValueError('Datetime must be in YYYY-MM-DD HH:MM format (e.g., 2025-02-09 14:30)')
        return v

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values:
            start = values['start_time']
            end = v
            if end <= start:
                raise ValueError('End time must be after start time')
        return v

class InstructorUnavailabilityCreate(InstructorUnavailabilityBase):
    pass

class InstructorUnavailability(InstructorUnavailabilityBase):
    id: int
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d %H:%M')
        }

class VehicleBase(BaseModel):
    vehicle_type: str
    plate_number: str
    model: str
    is_active: bool = True

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int

class InstructorBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., description="Phone number in E.164 format", pattern=PHONE_NUMBER_PATTERN)
    qualifications: List[str]
    weekly_availability: DaySchedule
    is_active: bool = True

class InstructorCreate(InstructorBase):
    pass

class Instructor(InstructorBase):
    id: int

class PackageBase(BaseModel):
    name: str
    hours: int
    vehicle_type: str
    price: float
    description: Optional[str] = None
    is_active: bool = True

class PackageCreate(PackageBase):
    pass

class Package(PackageBase):
    id: int

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(..., description="Phone number in E.164 format", pattern=PHONE_NUMBER_PATTERN)

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    created_at: datetime

class LessonBase(BaseModel):
    student_id: int
    instructor_id: int
    vehicle_id: int
    start_time: datetime
    duration: int
    status: str = 'scheduled'
    notes: Optional[str] = None
    student_package_id: int

    @validator('start_time')
    def convert_str_to_datetime(cls, v):
        if isinstance(v, str):
            try:
                # Try common formats
                formats = [
                    '%Y-%m-%d %H:%M',  # 2024-02-09 14:30
                    '%Y-%m-%d %-I:%M %p',  # 2024-02-09 2:30 PM
                    '%d/%m/%Y %H:%M',  # 09/02/2024 14:30
                    '%d/%m/%Y %-I:%M %p',  # 09/02/2024 2:30 PM
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(v, fmt)
                    except ValueError:
                        continue
                raise ValueError('Invalid datetime format')
            except Exception as e:
                raise ValueError(f'Invalid datetime format: {str(e)}')
        return v

class LessonCreate(LessonBase):
    pass

class Lesson(LessonBase):
    id: int
    created_at: datetime
    updated_at: datetime

class StudentPackageBase(BaseModel):
    student_id: int
    package_id: int
    hours_remaining: int

class StudentPackageCreate(StudentPackageBase):
    pass

class StudentPackage(StudentPackageBase):
    id: int
    purchase_date: datetime
