from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.db.connection import Database

class LessonService:
    def __init__(self, db: Database):
        self.db = db

    def schedule_lesson(self, lesson_data: dict) -> dict:
        """Schedule a new lesson after validating availability and requirements."""
        with self.db.get_cursor() as cur:
            # Validate student exists
            cur.execute("""
                SELECT id FROM students WHERE id = %(student_id)s
            """, {'student_id': lesson_data['student_id']})
            if not cur.fetchone():
                raise ValueError("Student not found")

            # Validate instructor exists and is active
            cur.execute("""
                SELECT id FROM instructors 
                WHERE id = %(instructor_id)s AND is_active = true
            """, {'instructor_id': lesson_data['instructor_id']})
            if not cur.fetchone():
                raise ValueError("Instructor not found or inactive")

            # Validate vehicle exists and is active
            cur.execute("""
                SELECT id FROM vehicles 
                WHERE id = %(vehicle_id)s AND is_active = true
            """, {'vehicle_id': lesson_data['vehicle_id']})
            if not cur.fetchone():
                raise ValueError("Vehicle not found or inactive")

            # Validate student package exists and belongs to the student
            cur.execute("""
                SELECT sp.id, sp.hours_remaining, p.vehicle_type 
                FROM student_packages sp
                JOIN packages p ON p.id = sp.package_id
                WHERE sp.id = %(student_package_id)s 
                AND sp.student_id = %(student_id)s
            """, {
                'student_package_id': lesson_data['student_package_id'],
                'student_id': lesson_data['student_id']
            })
            package = cur.fetchone()
            if not package:
                raise ValueError("Invalid package or package does not belong to the student")

            # Validate sufficient hours remaining
            required_hours = lesson_data['duration'] / 60
            if package['hours_remaining'] < required_hours:
                raise ValueError(f"Insufficient hours remaining in package. Required: {required_hours}, Available: {package['hours_remaining']}")

            # Check instructor availability
            if not self._is_instructor_available(
                lesson_data['instructor_id'],
                lesson_data['start_time'],
                lesson_data['duration']
            ):
                raise ValueError("Instructor is not available for this time slot")

            # Check vehicle availability
            if not self._is_vehicle_available(
                lesson_data['vehicle_id'],
                lesson_data['start_time'],
                lesson_data['duration']
            ):
                raise ValueError("Vehicle is not available for this time slot")

            # Validate lesson time is in the future
            if lesson_data['start_time'] <= datetime.now():
                raise ValueError("Lesson start time must be in the future")

            # Create the lesson
            try:
                cur.execute("""
                    INSERT INTO lessons (
                        student_id, instructor_id, vehicle_id, start_time, 
                        duration, status, notes, student_package_id
                    ) VALUES (
                        %(student_id)s, %(instructor_id)s, %(vehicle_id)s, 
                        %(start_time)s, %(duration)s, %(status)s, %(notes)s,
                        %(student_package_id)s
                    ) RETURNING *
                """, lesson_data)
                
                lesson = cur.fetchone()

                # Update remaining hours
                cur.execute("""
                    UPDATE student_packages 
                    SET hours_remaining = hours_remaining - %(hours)s
                    WHERE id = %(package_id)s
                    RETURNING hours_remaining
                """, {
                    'hours': required_hours,
                    'package_id': lesson_data['student_package_id']
                })
                
                updated_package = cur.fetchone()
                
                # Add additional info to the response
                lesson['hours_remaining'] = updated_package['hours_remaining']
                return lesson
                
            except Exception as e:
                raise ValueError(f"Failed to schedule lesson: {str(e)}")

    def get_available_slots(self, 
                          date: datetime, 
                          instructor_id: Optional[int] = None,
                          vehicle_type: Optional[str] = None) -> List[Dict]:
        """Get available time slots for scheduling lessons."""
        with self.db.get_cursor() as cur:
            query = """
                WITH time_slots AS (
                    SELECT generate_series(
                        %(start_time)s::timestamp,
                        %(end_time)s::timestamp,
                        '30 minutes'::interval
                    ) AS slot_time
                ),
                busy_instructors AS (
                    SELECT start_time, duration
                    FROM lessons
                    WHERE start_time::date = %(date)s::date
                    AND status != 'cancelled'
                    UNION
                    SELECT start_time, 
                           EXTRACT(EPOCH FROM (end_time - start_time))/60 as duration
                    FROM instructor_unavailability
                    WHERE start_time::date = %(date)s::date
                )
                SELECT ts.slot_time,
                       NOT EXISTS (
                           SELECT 1 FROM busy_instructors bi
                           WHERE bi.start_time <= ts.slot_time
                           AND bi.start_time + (bi.duration || ' minutes')::interval > ts.slot_time
                       ) as is_available
                FROM time_slots ts
                ORDER BY ts.slot_time;
            """
            
            cur.execute(query, {
                'date': date.date(),
                'start_time': datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=8),
                'end_time': datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=17)
            })
            
            return cur.fetchall()

    def _is_instructor_available(self, instructor_id: int, start_time: datetime, duration: int) -> bool:
        """Check if instructor is available for the given time slot."""
        with self.db.get_cursor() as cur:
            # Check existing lessons
            cur.execute("""
                SELECT 1
                FROM lessons
                WHERE instructor_id = %(instructor_id)s
                AND start_time < %(end_time)s
                AND start_time + (duration || ' minutes')::interval > %(start_time)s
                AND status != 'cancelled'
                LIMIT 1
            """, {
                'instructor_id': instructor_id,
                'start_time': start_time,
                'end_time': start_time + timedelta(minutes=duration)
            })
            
            if cur.fetchone():
                return False

            # Check instructor unavailability
            cur.execute("""
                SELECT 1
                FROM instructor_unavailability
                WHERE instructor_id = %(instructor_id)s
                AND start_time < %(end_time)s
                AND end_time > %(start_time)s
                LIMIT 1
            """, {
                'instructor_id': instructor_id,
                'start_time': start_time,
                'end_time': start_time + timedelta(minutes=duration)
            })
            
            if cur.fetchone():
                return False

            return True

    def _is_vehicle_available(self, vehicle_id: int, start_time: datetime, duration: int) -> bool:
        """Check if vehicle is available for the given time slot."""
        with self.db.get_cursor() as cur:
            # Check existing lessons
            cur.execute("""
                SELECT 1
                FROM lessons
                WHERE vehicle_id = %(vehicle_id)s
                AND start_time < %(end_time)s
                AND start_time + (duration || ' minutes')::interval > %(start_time)s
                AND status != 'cancelled'
                LIMIT 1
            """, {
                'vehicle_id': vehicle_id,
                'start_time': start_time,
                'end_time': start_time + timedelta(minutes=duration)
            })
            
            if cur.fetchone():
                return False

            return True

    def cancel_lesson(self, lesson_id: int, reason: str) -> dict:
        """Cancel a scheduled lesson."""
        with self.db.get_cursor() as cur:
            # Get lesson details
            cur.execute("""
                SELECT * FROM lessons WHERE id = %(lesson_id)s
            """, {'lesson_id': lesson_id})
            
            lesson = cur.fetchone()
            if not lesson:
                raise ValueError("Lesson not found")

            if lesson['status'] == 'cancelled':
                raise ValueError("Lesson is already cancelled")

            # Update lesson status
            cur.execute("""
                UPDATE lessons 
                SET status = 'cancelled',
                    notes = CASE 
                        WHEN notes IS NULL THEN %(reason)s
                        ELSE notes || E'\n' || %(reason)s
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %(lesson_id)s
                RETURNING *
            """, {
                'lesson_id': lesson_id,
                'reason': f"Cancelled: {reason}"
            })

            cancelled_lesson = cur.fetchone()

            # Refund hours to student package
            cur.execute("""
                UPDATE student_packages 
                SET hours_remaining = hours_remaining + %(hours)s
                WHERE id = %(package_id)s
            """, {
                'hours': lesson['duration'] / 60,
                'package_id': lesson['student_package_id']
            })

            return cancelled_lesson
