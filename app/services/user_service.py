from typing import List, Dict, Optional
import json
from app.db.connection import Database
from app.db.queries.users import (
    CREATE_INSTRUCTOR, GET_INSTRUCTOR, LIST_INSTRUCTORS, UPDATE_INSTRUCTOR,
    CREATE_STUDENT, GET_STUDENT, LIST_STUDENTS, UPDATE_STUDENT
)
from datetime import datetime

class UserService:
    def __init__(self, db: Database):
        self.db = db

    def _prepare_instructor_data(self, data: dict) -> dict:
        """Prepare instructor data for database insertion."""
        if 'weekly_availability' in data:
            data['weekly_availability'] = json.dumps(data['weekly_availability'])
        if 'qualifications' in data and isinstance(data['qualifications'], list):
            data['qualifications'] = list(data['qualifications'])
        return data

    def _process_instructor_result(self, result: dict) -> dict:
        """Process instructor result from database."""
        if result and 'weekly_availability' in result:
            if isinstance(result['weekly_availability'], str):
                result['weekly_availability'] = json.loads(result['weekly_availability'])
        return result

    # Instructor methods
    def create_instructor(self, instructor_data: dict) -> dict:
        """Create a new instructor."""
        prepared_data = self._prepare_instructor_data(instructor_data)
        with self.db.get_cursor() as cur:
            cur.execute(CREATE_INSTRUCTOR, prepared_data)
            result = cur.fetchone()
            return self._process_instructor_result(result)

    def get_instructor(self, instructor_id: int) -> Optional[dict]:
        """Get instructor by ID."""
        with self.db.get_cursor() as cur:
            cur.execute(GET_INSTRUCTOR, {'id': instructor_id})
            result = cur.fetchone()
            return self._process_instructor_result(result)

    def list_instructors(self) -> List[dict]:
        """List all active instructors."""
        with self.db.get_cursor() as cur:
            cur.execute(LIST_INSTRUCTORS)
            results = cur.fetchall()
            return [self._process_instructor_result(result) for result in results]

    def update_instructor(self, instructor_id: int, instructor_data: dict) -> Optional[dict]:
        """Update instructor details."""
        prepared_data = self._prepare_instructor_data(instructor_data)
        prepared_data['id'] = instructor_id
        with self.db.get_cursor() as cur:
            cur.execute(UPDATE_INSTRUCTOR, prepared_data)
            result = cur.fetchone()
            return self._process_instructor_result(result)

    def deactivate_instructor(self, instructor_id: int) -> Optional[dict]:
        """Deactivate an instructor."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE instructors 
                SET is_active = false 
                WHERE id = %(id)s
                RETURNING *
            """, {'id': instructor_id})
            result = cur.fetchone()
            return self._process_instructor_result(result)

    # Student methods
    def create_student(self, student_data: dict) -> dict:
        """Create a new student."""
        with self.db.get_cursor() as cur:
            cur.execute(CREATE_STUDENT, student_data)
            return cur.fetchone()

    def get_student(self, student_id: int) -> Optional[dict]:
        """Get student by ID with their package information."""
        with self.db.get_cursor() as cur:
            cur.execute(GET_STUDENT, {'id': student_id})
            return cur.fetchone()

    def list_students(self) -> List[dict]:
        """List all students."""
        with self.db.get_cursor() as cur:
            cur.execute(LIST_STUDENTS)
            return cur.fetchall()

    def update_student(self, student_id: int, student_data: dict) -> Optional[dict]:
        """Update student details."""
        student_data['id'] = student_id
        with self.db.get_cursor() as cur:
            cur.execute(UPDATE_STUDENT, student_data)
            return cur.fetchone()

    def get_student_lessons(self, student_id: int, start_date: str, end_date: str) -> List[dict]:
        """Get student's lesson history."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT l.*, i.name as instructor_name
                FROM lessons l
                JOIN instructors i ON l.instructor_id = i.id
                WHERE l.student_id = %(student_id)s
                AND l.start_time BETWEEN %(start_date)s AND %(end_date)s
                ORDER BY l.start_time DESC
            """, {
                'student_id': student_id,
                'start_date': start_date,
                'end_date': end_date
            })
            return cur.fetchall()

    def add_instructor_unavailability(self, unavailability_data: dict) -> dict:
        """Add a new instructor unavailability period."""
        with self.db.get_cursor() as cur:
            # First check if instructor exists and is active
            cur.execute("""
                SELECT id FROM instructors 
                WHERE id = %(instructor_id)s AND is_active = true
            """, {'instructor_id': unavailability_data['instructor_id']})
            
            if not cur.fetchone():
                raise ValueError("Instructor not found or inactive")

            # Check for overlapping unavailability periods
            cur.execute("""
                SELECT id FROM instructor_unavailability
                WHERE instructor_id = %(instructor_id)s
                AND (
                    (start_time <= %(start_time)s AND end_time > %(start_time)s)
                    OR (start_time < %(end_time)s AND end_time >= %(end_time)s)
                    OR (start_time >= %(start_time)s AND end_time <= %(end_time)s)
                )
            """, unavailability_data)

            if cur.fetchone():
                raise ValueError("This time period overlaps with an existing unavailability period")

            # Add the unavailability period
            cur.execute("""
                INSERT INTO instructor_unavailability (
                    instructor_id, start_time, end_time, reason
                ) VALUES (
                    %(instructor_id)s, %(start_time)s, %(end_time)s, %(reason)s
                ) RETURNING *
            """, unavailability_data)
            return cur.fetchone()

    def get_instructor_unavailability(self, instructor_id: int, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get instructor's unavailability periods within a date range."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM instructor_unavailability
                WHERE instructor_id = %(instructor_id)s
                AND start_time <= %(end_date)s
                AND end_time >= %(start_date)s
                ORDER BY start_time
            """, {
                'instructor_id': instructor_id,
                'start_date': start_date,
                'end_date': end_date
            })
            return cur.fetchall()

    def delete_instructor_unavailability(self, unavailability_id: int) -> bool:
        """Delete an instructor unavailability period."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                DELETE FROM instructor_unavailability
                WHERE id = %(id)s
                RETURNING id
            """, {'id': unavailability_id})
            return cur.fetchone() is not None

    def update_instructor_unavailability(self, unavailability_id: int, unavailability_data: dict) -> Optional[dict]:
        """Update an instructor unavailability period."""
        unavailability_data['id'] = unavailability_id
        
        with self.db.get_cursor() as cur:
            # Check if the unavailability period exists
            cur.execute("""
                SELECT instructor_id FROM instructor_unavailability
                WHERE id = %(id)s
            """, {'id': unavailability_id})
            
            existing = cur.fetchone()
            if not existing:
                return None

            # Check for overlapping periods (excluding the current one)
            cur.execute("""
                SELECT id FROM instructor_unavailability
                WHERE instructor_id = %(instructor_id)s
                AND id != %(id)s
                AND (
                    (start_time <= %(start_time)s AND end_time > %(start_time)s)
                    OR (start_time < %(end_time)s AND end_time >= %(end_time)s)
                    OR (start_time >= %(start_time)s AND end_time <= %(end_time)s)
                )
            """, unavailability_data)

            if cur.fetchone():
                raise ValueError("This time period overlaps with an existing unavailability period")

            # Update the unavailability period
            cur.execute("""
                UPDATE instructor_unavailability SET
                    start_time = %(start_time)s,
                    end_time = %(end_time)s,
                    reason = %(reason)s
                WHERE id = %(id)s
                RETURNING *
            """, unavailability_data)
            return cur.fetchone()
