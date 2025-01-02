from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db_cursor, init_db
from .models import User, Instructor, Vehicle, Appointment
from . import schemas
from .auth import create_access_token, get_current_user, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from .routers import appointments, instructors, auth
from datetime import timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Scheduling System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(instructors.router, prefix="/api")

@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: schemas.UserLogin):
    logger.info(f"Login attempt for email: {form_data.email}")
    
    with get_db_cursor() as cursor:
        user = User.get_by_email(cursor, form_data.email)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/appointments")
async def get_appointments(current_user: User = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        appointments = Appointment.get_all(cursor)
        return appointments

@app.post("/api/appointments")
async def create_appointment(
    appointment: schemas.AppointmentCreate,
    current_user: User = Depends(get_current_user)
):
    with get_db_cursor() as cursor:
        new_appointment = Appointment.create(
            cursor,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            student_name=appointment.student_name,
            student_email=appointment.student_email,
            instructor_id=appointment.instructor_id,
            vehicle_id=appointment.vehicle_id,
            status="scheduled"
        )
        return new_appointment

@app.get("/api/vehicles")
async def get_vehicles(current_user: User = Depends(get_current_user)):
    with get_db_cursor() as cursor:
        vehicles = Vehicle.get_all(cursor)
        return vehicles

@app.get("/")
def read_root():
    return {"message": "Welcome to the Scheduling System API"}
