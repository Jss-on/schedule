from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from ..schemas import AppointmentCreate, AppointmentUpdate, Appointment
from ..database import get_db_cursor
from ..auth import get_current_user

router = APIRouter()

@router.post("/appointments", response_model=Appointment)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        # Validate instructor availability
        cursor.execute(
            "SELECT id FROM instructors WHERE id = %s",
            (appointment.instructor_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Instructor not found")

        # Validate vehicle availability
        cursor.execute(
            "SELECT id FROM vehicles WHERE id = %s",
            (appointment.vehicle_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # Check for scheduling conflicts
        cursor.execute("""
            SELECT id FROM appointments 
            WHERE instructor_id = %s 
            AND start_time < %s 
            AND end_time > %s
        """, (
            appointment.instructor_id,
            appointment.end_time,
            appointment.start_time
        ))
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Scheduling conflict detected"
            )

        # Create the appointment
        cursor.execute("""
            INSERT INTO appointments (
                student_name, student_email, student_phone,
                start_time, end_time, instructor_id, vehicle_id,
                special_requirements, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id, student_name, student_email, student_phone,
                      start_time, end_time, instructor_id, vehicle_id,
                      special_requirements, status, created_at, updated_at
        """, (
            appointment.student_name,
            appointment.student_email,
            appointment.student_phone,
            appointment.start_time,
            appointment.end_time,
            appointment.instructor_id,
            appointment.vehicle_id,
            appointment.special_requirements,
            'scheduled'
        ))
        
        return cursor.fetchone()

@router.get("/appointments", response_model=List[Appointment])
async def read_appointments(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, student_name, student_email, student_phone,
                   start_time, end_time, instructor_id, vehicle_id,
                   special_requirements, status, created_at, updated_at
            FROM appointments
            ORDER BY start_time DESC
            OFFSET %s LIMIT %s
        """, (skip, limit))
        return cursor.fetchall()

@router.get("/appointments/{appointment_id}", response_model=Appointment)
async def read_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, student_name, student_email, student_phone,
                   start_time, end_time, instructor_id, vehicle_id,
                   special_requirements, status, created_at, updated_at
            FROM appointments
            WHERE id = %s
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if appointment is None:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment

@router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(
    appointment_id: int,
    appointment: AppointmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        # Check if appointment exists
        cursor.execute(
            "SELECT id FROM appointments WHERE id = %s",
            (appointment_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Update the appointment
        update_fields = []
        update_values = []
        
        # Build dynamic update query based on provided fields
        update_data = appointment.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                update_fields.append(f"{key} = %s")
                update_values.append(value)
        
        if update_fields:
            update_values.append(appointment_id)
            query = f"""
                UPDATE appointments 
                SET {", ".join(update_fields)}, updated_at = NOW()
                WHERE id = %s
                RETURNING id, student_name, student_email, student_phone,
                          start_time, end_time, instructor_id, vehicle_id,
                          special_requirements, status, created_at, updated_at
            """
            cursor.execute(query, update_values)
            return cursor.fetchone()

@router.delete("/appointments/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        cursor.execute(
            "DELETE FROM appointments WHERE id = %s RETURNING id",
            (appointment_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Appointment not found")
        return {"message": "Appointment deleted successfully"}
