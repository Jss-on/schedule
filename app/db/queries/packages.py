CREATE_PACKAGE = """
    INSERT INTO packages (name, hours, vehicle_type, price, description)
    VALUES (%(name)s, %(hours)s, %(vehicle_type)s, %(price)s, %(description)s)
    RETURNING id, name, hours, vehicle_type, price, description, is_active;
"""

GET_PACKAGE = """
    SELECT id, name, hours, vehicle_type, price, description, is_active
    FROM packages
    WHERE id = %(id)s;
"""

LIST_PACKAGES = """
    SELECT id, name, hours, vehicle_type, price, description, is_active
    FROM packages
    WHERE is_active = true
    ORDER BY name;
"""

UPDATE_PACKAGE = """
    UPDATE packages
    SET name = %(name)s,
        hours = %(hours)s,
        vehicle_type = %(vehicle_type)s,
        price = %(price)s,
        description = %(description)s,
        is_active = %(is_active)s
    WHERE id = %(id)s
    RETURNING id, name, hours, vehicle_type, price, description, is_active;
"""

CREATE_STUDENT_PACKAGE = """
    INSERT INTO student_packages (student_id, package_id, hours_remaining)
    VALUES (%(student_id)s, %(package_id)s, %(hours_remaining)s)
    RETURNING id, student_id, package_id, hours_remaining, purchase_date;
"""

GET_STUDENT_PACKAGE = """
    SELECT sp.id, sp.student_id, sp.package_id, sp.hours_remaining, sp.purchase_date,
           p.name as package_name, p.vehicle_type, p.price
    FROM student_packages sp
    JOIN packages p ON sp.package_id = p.id
    WHERE sp.id = %(id)s;
"""

LIST_STUDENT_PACKAGES = """
    SELECT sp.id, sp.student_id, sp.package_id, sp.hours_remaining, sp.purchase_date,
           p.name as package_name, p.vehicle_type, p.price
    FROM student_packages sp
    JOIN packages p ON sp.package_id = p.id
    WHERE sp.student_id = %(student_id)s
    ORDER BY sp.purchase_date DESC;
"""
