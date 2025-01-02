from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db_cursor
from ..auth import get_current_user
from ..schemas import InstructorCreate, InstructorResponse
from typing import List

router = APIRouter()

@router.post("/instructors", response_model=InstructorResponse)
async def create_instructor(instructor: InstructorCreate, current_user: dict = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO instructors (name, email, phone, specialization)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, email, phone, specialization, created_at, updated_at
        """, (instructor.name, instructor.email, instructor.phone, instructor.specialization))
        return cursor.fetchone()

@router.get("/instructors", response_model=List[InstructorResponse])
async def get_instructors(current_user: dict = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, email, phone, specialization, created_at, updated_at
            FROM instructors
            ORDER BY name
        """)
        return cursor.fetchall()

@router.get("/instructors/{instructor_id}", response_model=InstructorResponse)
async def get_instructor(instructor_id: int, current_user: dict = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, name, email, phone, specialization, created_at, updated_at
            FROM instructors
            WHERE id = %s
        """, (instructor_id,))
        instructor = cursor.fetchone()
        if instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return instructor

@router.put("/instructors/{instructor_id}", response_model=InstructorResponse)
async def update_instructor(
    instructor_id: int,
    instructor: InstructorCreate,
    current_user: dict = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        cursor.execute("""
            UPDATE instructors
            SET name = %s, email = %s, phone = %s, specialization = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, name, email, phone, specialization, created_at, updated_at
        """, (instructor.name, instructor.email, instructor.phone, instructor.specialization, instructor_id))
        updated_instructor = cursor.fetchone()
        if updated_instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return updated_instructor

@router.delete("/instructors/{instructor_id}")
async def delete_instructor(instructor_id: int, current_user: dict = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM instructors WHERE id = %s RETURNING id", (instructor_id,))
        deleted_instructor = cursor.fetchone()
        if deleted_instructor is None:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return {"message": "Instructor deleted successfully"}
