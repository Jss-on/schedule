from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
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

@router.get("/lessons/available-slots/")
async def get_available_slots(
    date: datetime,
    instructor_id: Optional[int] = None,
    vehicle_type: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Get available time slots for scheduling lessons."""
    try:
        lesson_service = LessonService(db)
        return lesson_service.get_available_slots(date, instructor_id, vehicle_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

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
