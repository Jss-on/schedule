from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime, timedelta
from app.db.connection import Database
from app.services.user_service import UserService
from app.schemas.models import (
    Instructor, InstructorCreate, InstructorBase,
    Student, StudentCreate, StudentBase,
    InstructorUnavailability, InstructorUnavailabilityCreate
)

router = APIRouter()

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

# Instructor routes
@router.post("/instructors/", response_model=Instructor)
async def create_instructor(
    instructor_data: InstructorCreate,
    db: Database = Depends(get_db)
):
    """Create a new instructor."""
    try:
        user_service = UserService(db)
        instructor_dict = instructor_data.model_dump()
        result = user_service.create_instructor(instructor_dict)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create instructor")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/instructors/{instructor_id}", response_model=Instructor)
async def get_instructor(
    instructor_id: int,
    db: Database = Depends(get_db)
):
    """Get instructor by ID."""
    user_service = UserService(db)
    instructor = user_service.get_instructor(instructor_id)
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return instructor

@router.get("/instructors/", response_model=List[Instructor])
async def list_instructors(
    db: Database = Depends(get_db)
):
    """List all active instructors."""
    user_service = UserService(db)
    return user_service.list_instructors()

@router.put("/instructors/{instructor_id}", response_model=Instructor)
async def update_instructor(
    instructor_id: int,
    instructor_data: InstructorBase,
    db: Database = Depends(get_db)
):
    """Update instructor details."""
    try:
        user_service = UserService(db)
        instructor_dict = instructor_data.model_dump()
        updated = user_service.update_instructor(instructor_id, instructor_dict)
        if not updated:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/instructors/{instructor_id}", response_model=Instructor)
async def deactivate_instructor(
    instructor_id: int,
    db: Database = Depends(get_db)
):
    """Deactivate an instructor."""
    try:
        user_service = UserService(db)
        deactivated = user_service.deactivate_instructor(instructor_id)
        if not deactivated:
            raise HTTPException(status_code=404, detail="Instructor not found")
        return deactivated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Student routes
@router.post("/students/", response_model=Student)
async def create_student(
    student_data: StudentCreate,
    db: Database = Depends(get_db)
):
    """Create a new student."""
    try:
        user_service = UserService(db)
        student_dict = student_data.model_dump()
        return user_service.create_student(student_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/students/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    db: Database = Depends(get_db)
):
    """Get student by ID."""
    user_service = UserService(db)
    student = user_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/students/", response_model=List[Student])
async def list_students(
    db: Database = Depends(get_db)
):
    """List all students."""
    user_service = UserService(db)
    return user_service.list_students()

@router.put("/students/{student_id}", response_model=Student)
async def update_student(
    student_id: int,
    student_data: StudentBase,
    db: Database = Depends(get_db)
):
    """Update student details."""
    try:
        user_service = UserService(db)
        student_dict = student_data.model_dump()
        updated = user_service.update_student(student_id, student_dict)
        if not updated:
            raise HTTPException(status_code=404, detail="Student not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/students/{student_id}/lessons")
async def get_student_lessons(
    student_id: int,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)", regex=r'^\d{4}-\d{2}-\d{2}$'),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)", regex=r'^\d{4}-\d{2}-\d{2}$'),
    db: Database = Depends(get_db)
):
    """
    Get student's lesson history.
    
    Parameters:
    - student_id: ID of the student
    - start_date: Start date in YYYY-MM-DD format (e.g., 2025-02-09)
    - end_date: End date in YYYY-MM-DD format (e.g., 2025-02-10)
    """
    try:
        # Convert date strings to datetime objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Set end date to end of day
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)

        user_service = UserService(db)
        lessons = user_service.get_student_lessons(student_id, start_date_obj, end_date_obj)
        if not lessons:
            raise HTTPException(status_code=404, detail="No lessons found")
        return lessons
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Please use YYYY-MM-DD format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Instructor unavailability routes
@router.post("/instructors/{instructor_id}/unavailability", response_model=InstructorUnavailability)
async def add_instructor_unavailability(
    instructor_id: int,
    unavailability_data: InstructorUnavailabilityCreate,
    db: Database = Depends(get_db)
):
    """Add a new instructor unavailability period."""
    try:
        user_service = UserService(db)
        data = unavailability_data.model_dump()
        # Add instructor_id to the data
        data['instructor_id'] = instructor_id
        return user_service.add_instructor_unavailability(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/instructors/{instructor_id}/unavailability", response_model=List[InstructorUnavailability])
async def get_instructor_unavailability(
    instructor_id: int,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)", regex=r'^\d{4}-\d{2}-\d{2}$'),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)", regex=r'^\d{4}-\d{2}-\d{2}$'),
    db: Database = Depends(get_db)
):
    """
    Get instructor's unavailability periods within a date range.
    
    Parameters:
    - instructor_id: ID of the instructor
    - start_date: Start date in YYYY-MM-DD format (e.g., 2025-02-09)
    - end_date: End date in YYYY-MM-DD format (e.g., 2025-02-10)
    """
    try:
        # Convert date strings to datetime objects
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Set end date to end of day
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)

        user_service = UserService(db)
        return user_service.get_instructor_unavailability(instructor_id, start_date_obj, end_date_obj)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Please use YYYY-MM-DD format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/instructors/unavailability/{unavailability_id}")
async def delete_instructor_unavailability(
    unavailability_id: int,
    db: Database = Depends(get_db)
):
    """Delete an instructor unavailability period."""
    try:
        user_service = UserService(db)
        if not user_service.delete_instructor_unavailability(unavailability_id):
            raise HTTPException(status_code=404, detail="Unavailability period not found")
        return {"message": "Unavailability period deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/instructors/unavailability/{unavailability_id}", response_model=InstructorUnavailability)
async def update_instructor_unavailability(
    unavailability_id: int,
    unavailability_data: InstructorUnavailabilityCreate,
    db: Database = Depends(get_db)
):
    """Update an instructor unavailability period."""
    try:
        user_service = UserService(db)
        data = unavailability_data.model_dump()
        result = user_service.update_instructor_unavailability(unavailability_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Unavailability period not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
