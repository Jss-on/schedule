from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.connection import Database
from app.services.vehicle_service import VehicleService
from app.schemas.models import Vehicle, VehicleCreate

router = APIRouter()

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@router.post("/vehicles/", response_model=Vehicle)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Database = Depends(get_db)
):
    """Create a new vehicle."""
    try:
        vehicle_service = VehicleService(db)
        return vehicle_service.create_vehicle(vehicle_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: int,
    db: Database = Depends(get_db)
):
    """Get vehicle by ID."""
    vehicle_service = VehicleService(db)
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.get("/vehicles/", response_model=List[Vehicle])
async def list_vehicles(
    db: Database = Depends(get_db)
):
    """List all active vehicles."""
    vehicle_service = VehicleService(db)
    return vehicle_service.list_vehicles()

@router.put("/vehicles/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleCreate,
    db: Database = Depends(get_db)
):
    """Update vehicle details."""
    try:
        vehicle_service = VehicleService(db)
        vehicle = vehicle_service.update_vehicle(vehicle_id, vehicle_data.model_dump())
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    db: Database = Depends(get_db)
):
    """Delete a vehicle (soft delete)."""
    try:
        vehicle_service = VehicleService(db)
        if not vehicle_service.delete_vehicle(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return {"message": "Vehicle deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
