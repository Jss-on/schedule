from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    COORDINATOR = "coordinator"
    INSTRUCTOR = "instructor"

@dataclass
class User:
    email: str
    hashed_password: str
    full_name: str
    role: str
    id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def create(cursor, email: str, hashed_password: str, full_name: str, role: str):
        cursor.execute(
            """
            INSERT INTO users (email, hashed_password, full_name, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id, email, hashed_password, full_name, role, is_active, created_at, updated_at
            """,
            (email, hashed_password, full_name, role)
        )
        result = cursor.fetchone()
        logger.info(f"Created user: {result}")
        return User(**result)

    @staticmethod
    def get_by_email(cursor, email: str):
        logger.info(f"Searching for user with email: {email}")
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        result = cursor.fetchone()
        logger.info(f"Database result: {result}")
        return User(**result) if result else None

@dataclass
class Instructor:
    user_id: int
    id: Optional[int] = None

    @staticmethod
    def create(cursor, user_id: int):
        cursor.execute(
            """
            INSERT INTO instructors (user_id)
            VALUES (%s)
            RETURNING id, user_id
            """,
            (user_id,)
        )
        return Instructor(**cursor.fetchone())

    @staticmethod
    def get_all(cursor):
        cursor.execute(
            """
            SELECT i.*, u.full_name, u.email
            FROM instructors i
            JOIN users u ON i.user_id = u.id
            """
        )
        return cursor.fetchall()

@dataclass
class Vehicle:
    model: str
    plate_number: str
    status: str
    id: Optional[int] = None

    @staticmethod
    def create(cursor, model: str, plate_number: str, status: str):
        cursor.execute(
            """
            INSERT INTO vehicles (model, plate_number, status)
            VALUES (%s, %s, %s)
            RETURNING id, model, plate_number, status
            """,
            (model, plate_number, status)
        )
        return Vehicle(**cursor.fetchone())

    @staticmethod
    def get_all(cursor):
        cursor.execute("SELECT * FROM vehicles")
        return cursor.fetchall()

@dataclass
class Appointment:
    start_time: datetime
    end_time: datetime
    student_name: str
    student_email: str
    instructor_id: int
    vehicle_id: int
    status: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @staticmethod
    def create(cursor, start_time: datetime, end_time: datetime, 
               student_name: str, student_email: str, 
               instructor_id: int, vehicle_id: int, status: str):
        cursor.execute(
            """
            INSERT INTO appointments 
            (start_time, end_time, student_name, student_email, 
             instructor_id, vehicle_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (start_time, end_time, student_name, student_email,
             instructor_id, vehicle_id, status)
        )
        return Appointment(**cursor.fetchone())

    @staticmethod
    def get_all(cursor):
        cursor.execute(
            """
            SELECT a.*, i.user_id, u.full_name as instructor_name,
                   v.model as vehicle_model, v.plate_number
            FROM appointments a
            JOIN instructors i ON a.instructor_id = i.id
            JOIN users u ON i.user_id = u.id
            JOIN vehicles v ON a.vehicle_id = v.id
            ORDER BY a.start_time
            """
        )
        return cursor.fetchall()

@dataclass
class InstructorAvailability:
    instructor_id: int
    day_of_week: int  # 0-6 for Monday-Sunday
    start_time: datetime
    end_time: datetime
    id: Optional[int] = None
    is_available: bool = True

@dataclass
class WaitingList:
    student_name: str
    student_email: str
    student_phone: str
    preferred_date: datetime
    id: Optional[int] = None
    special_requirements: Optional[str] = None
    status: str = "waiting"  # waiting, contacted, scheduled
    created_at: Optional[datetime] = None
