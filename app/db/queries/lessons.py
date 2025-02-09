CREATE_LESSON = """
    INSERT INTO lessons (
        student_id, instructor_id, vehicle_id, start_time, 
        duration, status, notes, student_package_id
    )
    VALUES (
        %(student_id)s, %(instructor_id)s, %(vehicle_id)s, 
        %(start_time)s, %(duration)s, %(status)s, %(notes)s,
        %(student_package_id)s
    )
    RETURNING id, student_id, instructor_id, vehicle_id, start_time, 
              duration, status, notes, created_at, updated_at, student_package_id;
"""

GET_LESSON = """
    SELECT l.*, 
           i.name as instructor_name,
           s.name as student_name,
           v.plate_number,
           v.model as vehicle_model
    FROM lessons l
    JOIN instructors i ON l.instructor_id = i.id
    JOIN students s ON l.student_id = s.id
    JOIN vehicles v ON l.vehicle_id = v.id
    WHERE l.id = %(id)s;
"""

LIST_LESSONS = """
    SELECT l.*, 
           i.name as instructor_name,
           s.name as student_name,
           v.plate_number,
           v.model as vehicle_model
    FROM lessons l
    JOIN instructors i ON l.instructor_id = i.id
    JOIN students s ON l.student_id = s.id
    JOIN vehicles v ON l.vehicle_id = v.id
    WHERE l.start_time >= %(start_date)s
    AND l.start_time < %(end_date)s
    ORDER BY l.start_time;
"""

UPDATE_LESSON_STATUS = """
    UPDATE lessons
    SET status = %(status)s,
        notes = CASE 
            WHEN notes IS NULL THEN %(notes)s
            ELSE notes || E'\n' || %(notes)s
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = %(id)s
    RETURNING id, student_id, instructor_id, vehicle_id, start_time, 
              duration, status, notes, created_at, updated_at, student_package_id;
"""

GET_INSTRUCTOR_SCHEDULE = """
    SELECT l.*, 
           s.name as student_name,
           v.plate_number,
           v.model as vehicle_model
    FROM lessons l
    JOIN students s ON l.student_id = s.id
    JOIN vehicles v ON l.vehicle_id = v.id
    WHERE l.instructor_id = %(instructor_id)s
    AND l.start_time >= %(start_date)s
    AND l.start_time < %(end_date)s
    AND l.status != 'cancelled'
    ORDER BY l.start_time;
"""

GET_STUDENT_SCHEDULE = """
    SELECT l.*, 
           i.name as instructor_name,
           v.plate_number,
           v.model as vehicle_model
    FROM lessons l
    JOIN instructors i ON l.instructor_id = i.id
    JOIN vehicles v ON l.vehicle_id = v.id
    WHERE l.student_id = %(student_id)s
    AND l.start_time >= %(start_date)s
    AND l.start_time < %(end_date)s
    ORDER BY l.start_time;
"""
