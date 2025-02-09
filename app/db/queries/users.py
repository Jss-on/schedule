CREATE_INSTRUCTOR = """
    INSERT INTO instructors (name, email, phone, qualifications, weekly_availability)
    VALUES (%(name)s, %(email)s, %(phone)s, %(qualifications)s, %(weekly_availability)s)
    RETURNING id, name, email, phone, qualifications, weekly_availability;
"""

GET_INSTRUCTOR = """
    SELECT id, name, email, phone, qualifications, weekly_availability, is_active
    FROM instructors
    WHERE id = %(id)s;
"""

LIST_INSTRUCTORS = """
    SELECT id, name, email, phone, qualifications, weekly_availability, is_active
    FROM instructors
    WHERE is_active = true
    ORDER BY name;
"""

UPDATE_INSTRUCTOR = """
    UPDATE instructors
    SET name = %(name)s,
        email = %(email)s,
        phone = %(phone)s,
        qualifications = %(qualifications)s,
        weekly_availability = %(weekly_availability)s,
        is_active = %(is_active)s
    WHERE id = %(id)s
    RETURNING id, name, email, phone, qualifications, weekly_availability, is_active;
"""

CREATE_STUDENT = """
    INSERT INTO students (name, email, phone)
    VALUES (%(name)s, %(email)s, %(phone)s)
    RETURNING id, name, email, phone, created_at;
"""

GET_STUDENT = """
    SELECT s.id, s.name, s.email, s.phone, s.created_at,
           COALESCE(json_agg(
               json_build_object(
                   'package_id', sp.package_id,
                   'hours_remaining', sp.hours_remaining,
                   'purchase_date', sp.purchase_date
               )
           ) FILTER (WHERE sp.id IS NOT NULL), '[]') as packages
    FROM students s
    LEFT JOIN student_packages sp ON s.id = sp.student_id
    WHERE s.id = %(id)s
    GROUP BY s.id, s.name, s.email, s.phone, s.created_at;
"""

LIST_STUDENTS = """
    SELECT id, name, email, phone, created_at
    FROM students
    ORDER BY name;
"""

UPDATE_STUDENT = """
    UPDATE students
    SET name = %(name)s,
        email = %(email)s,
        phone = %(phone)s
    WHERE id = %(id)s
    RETURNING id, name, email, phone, created_at;
"""
