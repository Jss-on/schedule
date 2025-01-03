from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas import VehicleCreate, Vehicle
from ..database import get_db_cursor
from ..auth import get_current_user
from ..models import Vehicle as VehicleModel

router = APIRouter()

@router.get("/vehicles", response_model=List[Vehicle])
async def get_vehicles(current_user: dict = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT id, make, model, year, plate_number, status, created_at, updated_at
            FROM vehicles
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()

@router.post("/vehicles", response_model=Vehicle)
async def create_vehicle(
    vehicle: VehicleCreate,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "coordinator"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and coordinators can create vehicles"
        )

    with get_db_cursor() as cursor:
        # Check if plate number already exists
        cursor.execute(
            "SELECT id FROM vehicles WHERE plate_number = %s",
            (vehicle.plate_number,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Vehicle with this plate number already exists"
            )

        # Create new vehicle
        cursor.execute("""
            INSERT INTO vehicles (make, model, year, plate_number, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, make, model, year, plate_number, status, created_at, updated_at
        """, (
            vehicle.make,
            vehicle.model,
            vehicle.year,
            vehicle.plate_number,
            vehicle.status or 'available'
        ))
        return cursor.fetchone()

@router.put("/vehicles/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: int,
    vehicle: VehicleCreate,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "coordinator"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and coordinators can update vehicles"
        )

    with get_db_cursor() as cursor:
        # Check if vehicle exists
        cursor.execute(
            "SELECT id FROM vehicles WHERE id = %s",
            (vehicle_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # Check if plate number already exists (excluding current vehicle)
        cursor.execute(
            "SELECT id FROM vehicles WHERE plate_number = %s AND id != %s",
            (vehicle.plate_number, vehicle_id)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Vehicle with this plate number already exists"
            )

        # Update vehicle
        cursor.execute("""
            UPDATE vehicles
            SET make = %s,
                model = %s,
                year = %s,
                plate_number = %s,
                status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, make, model, year, plate_number, status, created_at, updated_at
        """, (
            vehicle.make,
            vehicle.model,
            vehicle.year,
            vehicle.plate_number,
            vehicle.status or 'available',
            vehicle_id
        ))
        return cursor.fetchone()

@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "coordinator"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and coordinators can delete vehicles"
        )

    with get_db_cursor() as cursor:
        # Check if vehicle exists
        cursor.execute(
            "SELECT id FROM vehicles WHERE id = %s",
            (vehicle_id,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # Check if vehicle is being used in any appointments
        cursor.execute(
            "SELECT id FROM appointments WHERE vehicle_id = %s",
            (vehicle_id,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Cannot delete vehicle that is being used in appointments"
            )

        # Delete vehicle
        cursor.execute(
            "DELETE FROM vehicles WHERE id = %s",
            (vehicle_id,)
        )
        return {"message": "Vehicle deleted successfully"}
