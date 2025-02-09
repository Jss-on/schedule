# Simplified Driving School System Architecture

## Project Structure
```
driving_school/
├── app/
│   ├── api/                    # API routes
│   │   ├── users.py           
│   │   ├── packages.py        
│   │   └── lessons.py         
│   ├── services/              # Business logic
│   │   ├── user_service.py
│   │   ├── package_service.py
│   │   └── lesson_service.py
│   ├── db/                    # Database utilities
│   │   ├── connection.py      # Database connection handler
│   │   └── queries/          # SQL queries
│   │       ├── users.py
│   │       ├── packages.py
│   │       └── lessons.py
│   └── schemas/              # Pydantic schemas for request/response
│       ├── user.py
│       ├── package.py
│       └── lesson.py
└── main.py                   # FastAPI application entry point
```

## Core Components

### 1. Database Connection
```python
# db/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class Database:
    def __init__(self, config):
        self.config = config

    @contextmanager
    def get_cursor(self):
        conn = psycopg2.connect(**self.config)
        try:
            yield conn.cursor(cursor_factory=RealDictCursor)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
```

### 2. SQL Queries
```python
# db/queries/users.py
CREATE_INSTRUCTOR = """
    INSERT INTO instructors (name, email, phone, qualifications)
    VALUES (%(name)s, %(email)s, %(phone)s, %(qualifications)s)
    RETURNING id, name, email, phone, qualifications;
"""

GET_INSTRUCTOR = """
    SELECT id, name, email, phone, qualifications
    FROM instructors
    WHERE id = %(id)s;
"""

# db/queries/lessons.py
CREATE_LESSON = """
    INSERT INTO lessons (student_id, instructor_id, start_time, duration, status)
    VALUES (%(student_id)s, %(instructor_id)s, %(start_time)s, %(duration)s, %(status)s)
    RETURNING id, student_id, instructor_id, start_time, duration, status;
"""

GET_AVAILABLE_SLOTS = """
    SELECT ts.start_time, ts.duration
    FROM time_slots ts
    LEFT JOIN lessons l ON ts.start_time = l.start_time
    WHERE l.id IS NULL AND ts.start_time >= %(date)s::date
    ORDER BY ts.start_time;
"""
```

### 3. Services
```python
# services/lesson_service.py
from app.db.queries.lessons import CREATE_LESSON, GET_AVAILABLE_SLOTS

class LessonService:
    def __init__(self, db):
        self.db = db

    def schedule_lesson(self, lesson_data: dict) -> dict:
        with self.db.get_cursor() as cur:
            cur.execute(CREATE_LESSON, lesson_data)
            return cur.fetchone()

    def get_available_slots(self, date: str) -> list:
        with self.db.get_cursor() as cur:
            cur.execute(GET_AVAILABLE_SLOTS, {'date': date})
            return cur.fetchall()

# services/package_service.py
class PackageService:
    def __init__(self, db):
        self.db = db

    def create_package(self, package_data: dict) -> dict:
        with self.db.get_cursor() as cur:
            cur.execute(CREATE_PACKAGE, package_data)
            return cur.fetchone()
```

### 4. API Routes
```python
# api/lessons.py
from fastapi import APIRouter, Depends
from app.schemas.lesson import LessonCreate, LessonResponse
from app.db.connection import Database
from app.services.lesson_service import LessonService

router = APIRouter()

def get_db():
    return Database(config={
        "dbname": "driving_school",
        "user": "user",
        "password": "password",
        "host": "db"
    })

@router.post("/lessons/", response_model=LessonResponse)
def create_lesson(
    lesson_data: LessonCreate,
    db: Database = Depends(get_db)
):
    lesson_service = LessonService(db)
    return lesson_service.schedule_lesson(lesson_data.dict())
```

### 5. Database Schema
```sql
-- Initial database schema
CREATE TABLE instructors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    qualifications TEXT[]
);

CREATE TABLE packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hours INTEGER NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id)
);
```

## Key Features
- Direct database access with psycopg2
- SQL queries organized by domain
- Connection pooling and cursor management
- Clean separation of concerns
- Type validation with Pydantic schemas
- Efficient database operations