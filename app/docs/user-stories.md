[# User Stories and API Endpoints

## Admin User Stories

### Package Management
1. As an admin, I want to create a new driving lesson package
   ```
   POST /api/packages
   {
       "name": "Basic Manual",
       "hours": 10,
       "vehicle_type": "manual",
       "price": 20000,
       "description": "10 hours manual transmission course"
   }
   ```

2. As an admin, I want to view all available packages
   ```
   GET /api/packages
   ```

3. As an admin, I want to modify an existing package
   ```
   PUT /api/packages/{package_id}
   ```

### Instructor Management
1. As an admin, I want to create a new instructor account
   ```
   POST /api/instructors
   {
       "name": "John Doe",
       "email": "john@example.com",
       "phone": "+63999999999",
       "qualifications": ["manual", "automatic"]
   }
   ```

2. As an admin, I want to set instructor availability
   ```
   POST /api/instructors/{instructor_id}/availability
   {
       "schedule": [
           {
               "day": "monday",
               "time_slots": [
                   {"start": "09:00", "end": "12:00"},
                   {"start": "13:00", "end": "16:00"}
               ]
           }
       ]
   }
   ```

3. As an admin, I want to mark instructor as unavailable for specific dates
   ```
   POST /api/instructors/{instructor_id}/unavailable-dates
   {
       "dates": ["2025-02-10", "2025-02-11"],
       "reason": "Personal leave"
   }
   ```

### Schedule Management
1. As an admin, I want to schedule a driving lesson
   ```
   POST /api/lessons
   {
       "student_id": "123",
       "instructor_id": "456",
       "date": "2025-02-15",
       "start_time": "09:00",
       "duration": 3,
       "vehicle_type": "manual"
   }
   ```

2. As an admin, I want to view available time slots
   ```
   GET /api/schedule/available-slots
   Query params: date, vehicle_type
   ```

3. As an admin, I want to view all scheduled lessons
   ```
   GET /api/lessons
   Query params: date_from, date_to
   ```

## Student User Stories

1. As a student, I want to view my remaining hours
   ```
   GET /api/students/{student_id}/remaining-hours
   ```

2. As a student, I want to view my scheduled lessons
   ```
   GET /api/students/{student_id}/lessons
   ```

3. As a student, I want to request cancellation of a lesson
   ```
   POST /api/lessons/{lesson_id}/cancel-request
   {
       "reason": "Emergency appointment"
   }
   ```

## Instructor User Stories

1. As an instructor, I want to view my assigned lessons
   ```
   GET /api/instructors/{instructor_id}/lessons
   Query params: date_from, date_to
   ```

2. As an instructor, I want to view my schedule
   ```
   GET /api/instructors/{instructor_id}/schedule
   Query params: date
   ```

## Student Management

1. As an admin, I want to enroll a student in a package
   ```
   POST /api/enrollments
   {
       "student_id": "123",
       "package_id": "456",
       "start_date": "2025-02-15"
   }
   ```

2. As an admin, I want to view student progress
   ```
   GET /api/students/{student_id}/progress
   ```

## Common API Response Structure
```python
{
    "status": "success/error",
    "data": {
        # Response data here
    },
    "message": "Success/Error message",
    "metadata": {
        "timestamp": "2025-02-09T10:00:00Z",
        "request_id": "uuid-here"
    }
}
```

## Error Handling
- All endpoints should return appropriate HTTP status codes
- Common error responses:
  - 400: Bad Request (invalid input)
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Resource Not Found
  - 409: Conflict (e.g., double booking)
  - 500: Internal Server Error

## Authentication and Authorization
- All endpoints require authentication except public endpoints
- JWT-based authentication
- Role-based access control:
  - ADMIN: Full access
  - INSTRUCTOR: Limited to their own schedule and lessons
  - STUDENT: Limited to their own lessons and package details