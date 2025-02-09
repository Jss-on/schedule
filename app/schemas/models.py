from datetime import datetime, date, time
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field, validator
import re

def validate_phone(v: str) -> str:
    if not re.match(r'^\+?1?\d{9,15}$', v):
        raise ValueError('Invalid phone number')
    return v

class TimeSlot(BaseModel):
    start: str
    end: str

    @validator('start', 'end')
    def validate_time_format(cls, v):
        try:
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', v):
                raise ValueError('Time must be in HH:MM format')
            return v
        except Exception as e:
            raise ValueError(f'Invalid time format: {str(e)}')

class DaySchedule(BaseModel):
    monday: Optional[List[TimeSlot]] = []
    tuesday: Optional[List[TimeSlot]] = []
    wednesday: Optional[List[TimeSlot]] = []
    thursday: Optional[List[TimeSlot]] = []
    friday: Optional[List[TimeSlot]] = []
    saturday: Optional[List[TimeSlot]] = []
    sunday: Optional[List[TimeSlot]] = []

class InstructorUnavailabilityBase(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: Optional[str] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class InstructorUnavailabilityCreate(InstructorUnavailabilityBase):
    pass

class InstructorUnavailability(InstructorUnavailabilityBase):
    id: int
    created_at: datetime

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
    phone: str = Field(..., description="Phone number in E.164 format", pattern=r'^\+?1?\d{9,15}$')
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
    phone: str = Field(..., description="Phone number in E.164 format", pattern=r'^\+?1?\d{9,15}$')

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
