# Driving School Scheduling System

A comprehensive API-based system for managing driving school operations, built with FastAPI and PostgreSQL.

## Features

- Instructor Management
  - Create and manage instructor profiles
  - Track instructor qualifications
  - Manage instructor availability
  - View instructor schedules

- Student Management
  - Student registration and profile management
  - Track student progress
  - View lesson history
  - Manage student packages

- Package Management
  - Create and manage lesson packages
  - Track package hours
  - Assign packages to students
  - Monitor remaining hours

- Lesson Scheduling
  - Schedule driving lessons
  - Prevent double-booking
  - Check instructor and vehicle availability
  - Handle lesson cancellations
  - View available time slots

- Vehicle Management
  - Track vehicle availability
  - Manage vehicle maintenance
  - Vehicle type assignment

## Tech Stack

- FastAPI (Python web framework)
- PostgreSQL (Database)
- Pydantic (Data validation)
- psycopg2 (PostgreSQL adapter)
- Docker and Docker Compose

## Project Structure

```
driving_school/
├── app/
│   ├── api/              # API routes
│   │   ├── users.py     
│   │   ├── packages.py  
│   │   └── lessons.py   
│   ├── services/        # Business logic
│   │   ├── user_service.py
│   │   ├── package_service.py
│   │   └── lesson_service.py
│   ├── db/              # Database utilities
│   │   ├── connection.py
│   │   ├── schema.sql
│   │   └── queries/    
│   └── schemas/        # Pydantic models
│       └── models.py
├── docker-compose.yml   # Docker composition
├── Dockerfile          # Docker build file
├── requirements.txt    # Python dependencies
└── main.py            # Application entry point
```

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 16
- Python 3.11+

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd driving-school
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The API will be available at:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PgAdmin: http://localhost:5050

## API Documentation

The API documentation is available at `/docs` when the server is running. It provides:
- Interactive API documentation
- Request/response schemas
- Example requests
- Authentication information

## Environment Variables

Configure the following environment variables in docker-compose.yml or .env file:

```env
DB_HOST=db
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=driving_school_db
DB_PORT=5432
```

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

## Database Management

- PgAdmin is available at http://localhost:5050
- Default credentials:
  - Email: admin@admin.com
  - Password: admin123

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
