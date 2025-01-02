# Scheduling System

A full-stack application for managing test drive appointments, built with FastAPI, PostgreSQL, and React.

## Features

- Calendar view of appointments
- Manage test drive appointments
- Instructor schedule management
- Vehicle allocation
- User authentication and authorization
- Real-time availability checking
- Automated notifications
- Waiting list management

## Tech Stack

### Backend
- FastAPI (Python web framework)
- PostgreSQL (Database)
- psycopg2 (PostgreSQL adapter)
- JWT Authentication
- Pydantic (Data validation)

### Frontend
- React
- React Router
- Axios (HTTP client)
- Modern CSS

## Prerequisites

- Python 3.8+
- Node.js 14+
- Docker and Docker Compose

## Setup and Running the Application

1. Clone the repository:
```bash
git clone <repository-url>
cd schedule
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

This will start all services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- pgAdmin: http://localhost:5050

## Default Credentials

### Application Login
- Email: admin@example.com
- Password: admin123

### pgAdmin Access
1. Visit http://localhost:5050
2. Login credentials:
   - Email: admin@admin.com
   - Password: admin123

3. To add your database server in pgAdmin:
   - Click "Add New Server"
   - In "General" tab:
     - Name: Any name (e.g., "Schedule DB")
   - In "Connection" tab:
     - Host: db
     - Port: 5432
     - Database: schedule_db
     - Username: postgres
     - Password: postgres

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

The application uses Docker volumes for development, so any changes you make to the source code will be reflected immediately:
- Frontend changes will trigger automatic rebuild
- Backend changes will trigger automatic reload

## Environment Variables

The following environment variables are configured in docker-compose.yml:

### Backend
- DB_HOST=db
- DB_USER=postgres
- DB_PASSWORD=postgres
- DB_NAME=schedule_db
- SECRET_KEY=your-secret-key-here
- ALGORITHM=HS256
- ACCESS_TOKEN_EXPIRE_MINUTES=30

### Frontend
- REACT_APP_API_URL=http://localhost:8000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
