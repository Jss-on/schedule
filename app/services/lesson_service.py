from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.db.connection import Database
from datetime import time
import os

class LessonService:
    def __init__(self, db: Database):
        self.db = db
        # Business hours
        self.business_hours_start = int(os.getenv('BUSINESS_HOURS_START', '8'))
        self.business_hours_end = int(os.getenv('BUSINESS_HOURS_END', '17'))
        
        # Time slot settings
        self.time_slot_interval = int(os.getenv('TIME_SLOT_INTERVAL', '30'))
        self.min_lesson_duration = int(os.getenv('MIN_LESSON_DURATION', '30'))
        self.max_lesson_duration = int(os.getenv('MAX_LESSON_DURATION', '180'))
        
        # Pagination settings
        self.default_page_size = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
        self.max_page_size = int(os.getenv('MAX_PAGE_SIZE', '100'))

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
        try:
            with self.db.get_cursor() as cur:
                # Build the base query
                query = """
                    WITH time_slots AS (
                        SELECT generate_series(
                            %(start_time)s::timestamp,
                            %(end_time)s::timestamp,
                            %(interval)s::interval
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
                
                # Calculate start and end times for the day using environment variables
                start_time = datetime.combine(date.date(), time(hour=self.business_hours_start))
                end_time = datetime.combine(date.date(), time(hour=self.business_hours_end))
                
                params = {
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval': f"{self.time_slot_interval} minutes"
                }

                try:
                    cur.execute(query, params)
                    slots = []
                    for row in cur.fetchall():
                        slots.append({
                            'time': row['slot_time'].strftime('%Y-%m-%d %H:%M'),
                            'is_available': row['is_available']
                        })
                    return slots
                except Exception as e:
                    print(f"Error executing available slots query: {str(e)}")
                    print(f"Query: {query}")
                    print(f"Params: {params}")
                    raise ValueError(f"Failed to get available slots: {str(e)}")

        except Exception as e:
            print(f"Error in get_available_slots: {str(e)}")
            raise ValueError(f"Failed to get available slots: {str(e)}")

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

    def get_lessons(self, 
                   filters: Dict = None,
                   page: int = 1,
                   per_page: Optional[int] = None) -> Dict:
        """Get a paginated list of lessons with optional filters."""
        try:
            if per_page is None:
                per_page = self.default_page_size
            elif per_page > self.max_page_size:
                per_page = self.max_page_size

            with self.db.get_cursor() as cur:
                # Build the base query
                query = """
                    SELECT 
                        l.id,
                        l.start_time,
                        l.duration,
                        l.status,
                        l.notes,
                        l.created_at,
                        s.id as student_id,
                        s.name as student_name,
                        i.id as instructor_id,
                        i.name as instructor_name,
                        v.vehicle_type,
                        sp.id as student_package_id,
                        p.name as package_name
                    FROM lessons l
                    JOIN students s ON s.id = l.student_id
                    JOIN instructors i ON i.id = l.instructor_id
                    JOIN vehicles v ON v.id = l.vehicle_id
                    JOIN student_packages sp ON sp.id = l.student_package_id
                    JOIN packages p ON p.id = sp.package_id
                """
                conditions = []
                params = {}

                # Add filters
                if filters:
                    for key, value in filters.items():
                        if key == 'date_from':
                            conditions.append("l.start_time >= %(date_from)s::timestamp")
                            params['date_from'] = value.strftime('%Y-%m-%d %H:%M:%S')
                        elif key == 'date_to':
                            conditions.append("l.start_time <= %(date_to)s::timestamp")
                            params['date_to'] = value.strftime('%Y-%m-%d %H:%M:%S')
                        elif key == 'instructor_id':
                            conditions.append("l.instructor_id = %(instructor_id)s")
                            params['instructor_id'] = value
                        elif key == 'student_id':
                            conditions.append("l.student_id = %(student_id)s")
                            params['student_id'] = value
                        elif key == 'status':
                            conditions.append("l.status = %(status)s")
                            params['status'] = value

                # Add WHERE clause if there are conditions
                where_clause = ""
                if conditions:
                    where_clause = " WHERE " + " AND ".join(conditions)

                # Get total count first
                count_query = f"""
                    SELECT COUNT(*)
                    FROM lessons l
                    JOIN students s ON s.id = l.student_id
                    JOIN instructors i ON i.id = l.instructor_id
                    JOIN vehicles v ON v.id = l.vehicle_id
                    JOIN student_packages sp ON sp.id = l.student_package_id
                    JOIN packages p ON p.id = sp.package_id
                    {where_clause}
                """
                try:
                    cur.execute(count_query, params)
                    total = cur.fetchone()['count']
                except Exception as e:
                    print(f"Error executing count query: {str(e)}")
                    print(f"Query: {count_query}")
                    print(f"Params: {params}")
                    raise ValueError(f"Failed to get lesson count: {str(e)}")

                # If no results found, return empty response
                if total == 0:
                    return {
                        "lessons": [],
                        "total": 0,
                        "page": page,
                        "per_page": per_page
                    }

                # Add pagination to the main query
                query += where_clause
                query += " ORDER BY l.start_time DESC"
                query += " LIMIT %(limit)s OFFSET %(offset)s"
                params['limit'] = per_page
                params['offset'] = (page - 1) * per_page

                # Execute main query
                try:
                    cur.execute(query, params)
                    lessons = []
                    for row in cur.fetchall():
                        lessons.append({
                            "id": row['id'],
                            "student": {
                                "id": row['student_id'],
                                "name": row['student_name']
                            },
                            "instructor": {
                                "id": row['instructor_id'],
                                "name": row['instructor_name']
                            },
                            "package": {
                                "id": row['student_package_id'],
                                "name": row['package_name']
                            },
                            "start_time": row['start_time'].isoformat(),
                            "duration": row['duration'],
                            "status": row['status'],
                            "vehicle_type": row['vehicle_type'],
                            "notes": row['notes'],
                            "created_at": row['created_at'].isoformat()
                        })

                    return {
                        "lessons": lessons,
                        "total": total,
                        "page": page,
                        "per_page": per_page
                    }
                except Exception as e:
                    print(f"Error executing main query: {str(e)}")
                    print(f"Query: {query}")
                    print(f"Params: {params}")
                    raise ValueError(f"Failed to get lessons: {str(e)}")

        except Exception as e:
            print(f"Error in get_lessons: {str(e)}")
            raise ValueError(f"Failed to get lessons: {str(e)}")
