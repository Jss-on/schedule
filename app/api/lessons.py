from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.db.connection import Database
from app.services.lesson_service import LessonService
from app.schemas.models import LessonCreate, Lesson

router = APIRouter()

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@router.post("/lessons/", response_model=Lesson)
async def create_lesson(
    lesson_data: LessonCreate,
    db: Database = Depends(get_db)
):
    """Create a new lesson."""
    try:
        lesson_service = LessonService(db)
        return lesson_service.schedule_lesson(lesson_data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/lessons/")
async def get_lessons(
    date_from: Optional[str] = Query(None, description="Filter lessons from this date (YYYY-MM-DD)", regex=r'^\d{4}-\d{2}-\d{2}$'),
    date_to: Optional[str] = Query(None, description="Filter lessons until this date (YYYY-MM-DD)", regex=r'^\d{4}-\d{2}-\d{2}$'),
    instructor_id: Optional[int] = Query(None, description="Filter by instructor ID"),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    status: Optional[str] = Query(None, description="Filter by lesson status (scheduled, completed, cancelled)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Database = Depends(get_db)
):
    """
    Get all scheduled lessons with optional filters.
    
    Parameters:
    - date_from: Start date in YYYY-MM-DD format (e.g., 2025-02-09)
    - date_to: End date in YYYY-MM-DD format (e.g., 2025-02-10)
    - instructor_id: Optional instructor ID to filter lessons
    - student_id: Optional student ID to filter lessons
    - status: Optional lesson status (scheduled, completed, cancelled)
    - page: Page number for pagination
    - per_page: Number of items per page
    
    Returns a paginated list of lessons with their associated student, instructor, and package information.
    """
    try:
        # Convert date strings to datetime objects if provided
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Dates must be in YYYY-MM-DD format (e.g., 2025-02-09)"
            )
        
        # If date_to is provided, set it to end of day
        if date_to_obj:
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)

        # Validate instructor_id if provided
        if instructor_id:
            with db.get_cursor() as cur:
                cur.execute("SELECT id FROM instructors WHERE id = %s", (instructor_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Instructor not found")

        # Validate student_id if provided
        if student_id:
            with db.get_cursor() as cur:
                cur.execute("SELECT id FROM students WHERE id = %s", (student_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Student not found")

        # Validate status if provided
        valid_statuses = ['scheduled', 'completed', 'cancelled']
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        lesson_service = LessonService(db)
        try:
            return lesson_service.get_lessons(
                date_from=date_from_obj,
                date_to=date_to_obj,
                instructor_id=instructor_id,
                student_id=student_id,
                status=status,
                page=page,
                per_page=per_page
            )
        except Exception as service_error:
            print(f"Error in lesson_service.get_lessons: {str(service_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving lessons: {str(service_error)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in get_lessons endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/lessons/available-slots/")
async def get_available_slots(
    date: str = Query(..., description="Date in YYYY-MM-DD format", regex=r'^\d{4}-\d{2}-\d{2}$'),
    instructor_id: Optional[int] = Query(None, description="Filter slots by instructor ID"),
    vehicle_type: Optional[str] = Query(None, description="Filter slots by vehicle type"),
    db: Database = Depends(get_db)
):
    """
    Get available time slots for scheduling lessons.
    
    Parameters:
    - date: Date in YYYY-MM-DD format (e.g., 2025-02-09)
    - instructor_id: Optional instructor ID to filter slots
    - vehicle_type: Optional vehicle type to filter slots
    """
    try:
        # Convert string date to datetime at midnight
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        lesson_service = LessonService(db)
        return lesson_service.get_available_slots(date_obj, instructor_id, vehicle_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Please use YYYY-MM-DD format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/lessons/{lesson_id}/cancel")
async def cancel_lesson(
    lesson_id: int,
    reason: str,
    db: Database = Depends(get_db)
):
    """Cancel a scheduled lesson."""
    try:
        lesson_service = LessonService(db)
        return lesson_service.cancel_lesson(lesson_id, reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
