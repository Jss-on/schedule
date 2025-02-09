import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api import lessons, users, packages, vehicles
from datetime import datetime

# Create FastAPI application
app = FastAPI(
    title="Driving School Scheduling System",
    description="API for managing driving school schedules, lessons, and resources",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(packages.router, prefix="/api/v1", tags=["packages"])
app.include_router(lessons.router, prefix="/api/v1", tags=["lessons"])
app.include_router(vehicles.router, prefix="/api/v1", tags=["vehicles"])

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Driving School Scheduling System API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "status": "operational",
        "endpoints": {
            "users": "/api/v1/users",
            "packages": "/api/v1/packages",
            "lessons": "/api/v1/lessons"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
