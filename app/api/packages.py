from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.connection import Database
from app.services.package_service import PackageService
from app.schemas.models import (
    PackageCreate, Package, PackageBase,
    StudentPackageCreate, StudentPackage
)

router = APIRouter()

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@router.post("/packages/", response_model=Package)
async def create_package(
    package_data: PackageCreate,
    db: Database = Depends(get_db)
):
    """Create a new lesson package."""
    try:
        package_service = PackageService(db)
        return package_service.create_package(package_data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/packages/{package_id}", response_model=Package)
async def get_package(
    package_id: int,
    db: Database = Depends(get_db)
):
    """Get package by ID."""
    package_service = PackageService(db)
    package = package_service.get_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@router.get("/packages/", response_model=List[Package])
async def list_packages(
    db: Database = Depends(get_db)
):
    """List all active packages."""
    package_service = PackageService(db)
    return package_service.list_packages()

@router.put("/packages/{package_id}", response_model=Package)
async def update_package(
    package_id: int,
    package_data: PackageBase,
    db: Database = Depends(get_db)
):
    """Update package details."""
    package_service = PackageService(db)
    package = package_service.update_package(package_id, package_data.dict())
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@router.delete("/packages/{package_id}", response_model=Package)
async def deactivate_package(
    package_id: int,
    db: Database = Depends(get_db)
):
    """Deactivate a package."""
    package_service = PackageService(db)
    package = package_service.deactivate_package(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@router.post("/students/{student_id}/packages", response_model=StudentPackage)
async def assign_package_to_student(
    student_id: int,
    package_id: int,
    db: Database = Depends(get_db)
):
    """Assign a package to a student."""
    try:
        package_service = PackageService(db)
        return package_service.assign_package_to_student(student_id, package_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/students/{student_id}/packages", response_model=List[StudentPackage])
async def list_student_packages(
    student_id: int,
    db: Database = Depends(get_db)
):
    """List all packages assigned to a student."""
    package_service = PackageService(db)
    return package_service.list_student_packages(student_id)

@router.get("/student-packages/{student_package_id}", response_model=StudentPackage)
async def get_student_package(
    student_package_id: int,
    db: Database = Depends(get_db)
):
    """Get student package by ID."""
    package_service = PackageService(db)
    student_package = package_service.get_student_package(student_package_id)
    if not student_package:
        raise HTTPException(status_code=404, detail="Student package not found")
    return student_package
