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
schedule/
├── app/                  # Backend application
│   ├── api/             # API routes
│   │   ├── lessons.py   # Lesson management endpoints
│   │   ├── packages.py  # Package management endpoints
│   │   ├── users.py     # User management endpoints
│   │   └── vehicles.py  # Vehicle management endpoints
│   ├── db/              # Database related files
│   │   ├── queries/     # SQL queries organized by domain
│   │   │   ├── lessons.py
│   │   │   ├── packages.py
│   │   │   └── users.py
│   │   ├── connection.py # Database connection handling
│   │   ├── init-db.sh   # Database initialization script
│   │   └── schema.sql   # Database schema definition
│   ├── docs/            # Project documentation
│   │   ├── requirements.md
│   │   ├── system architecture.md
│   │   ├── system architecture.svg
│   │   └── user-stories.md
│   ├── schemas/         # Data validation models
│   │   └── models.py    # Pydantic models for data validation
│   └── services/        # Business logic layer
│       ├── lesson_service.py
│       ├── package_service.py
│       ├── user_service.py
│       └── vehicle_service.py
├── frontend/           # React frontend application
│   ├── public/         # Static assets
│   ├── src/           
│   │   ├── components/ # React components
│   │   │   ├── AppointmentForm.js
│   │   │   ├── Calendar.js
│   │   │   ├── Dashboard.js
│   │   │   └── ...
│   │   └── App.js     # Main application component
│   ├── Dockerfile     # Frontend container configuration
│   ├── nginx.conf     # Nginx configuration for serving frontend
│   └── package.json   # Frontend dependencies
├── docker-compose.yml  # Docker services configuration
├── Dockerfile         # Backend container configuration
├── README.md         # Project documentation
└── requirements.txt  # Python dependencies
```

### Directory Overview

- `app/`: Backend application built with FastAPI
  - `api/`: REST API endpoints organized by domain
  - `db/`: Database related code and migrations
  - `docs/`: Project documentation and architecture diagrams
  - `schemas/`: Data validation and serialization models
  - `services/`: Business logic implementation

- `frontend/`: React-based web interface
  - `src/components/`: Reusable React components
  - `public/`: Static assets and HTML template
  
- Root level configuration files for Docker, Python dependencies, and documentation

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

## Date and Time Formats

The system accepts multiple date and time formats for user convenience:

### Time Formats (for daily schedules)
- 24-hour format: `HH:MM` (e.g., "14:30")
- 12-hour format: `H:MM AM/PM` (e.g., "2:30 PM")

### Date-Time Formats (for lessons and unavailability)
- ISO format with 24-hour time: `YYYY-MM-DD HH:MM` (e.g., "2024-02-09 14:30")
- ISO format with 12-hour time: `YYYY-MM-DD H:MM AM/PM` (e.g., "2024-02-09 2:30 PM")
- UK/EU format with 24-hour time: `DD/MM/YYYY HH:MM` (e.g., "09/02/2024 14:30")
- UK/EU format with 12-hour time: `DD/MM/YYYY H:MM AM/PM` (e.g., "09/02/2024 2:30 PM")

All times are validated to ensure:
- End times occur after start times
- Times are within valid ranges
- No scheduling conflicts occur

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
