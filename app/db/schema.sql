-- Initial database schema
CREATE TABLE instructors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    qualifications TEXT[],
    weekly_availability JSONB,  -- Store weekly recurring availability
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE instructor_unavailability (
    id SERIAL PRIMARY KEY,
    instructor_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id)
);

CREATE TABLE packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hours INTEGER NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student_packages (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    package_id INTEGER NOT NULL REFERENCES packages(id),
    hours_remaining INTEGER NOT NULL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (package_id) REFERENCES packages(id)
);

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    vehicle_type VARCHAR(20) NOT NULL,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    model VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL, -- in minutes
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    student_package_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (student_package_id) REFERENCES student_packages(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_lessons_student_id ON lessons(student_id);
CREATE INDEX idx_lessons_instructor_id ON lessons(instructor_id);
CREATE INDEX idx_lessons_vehicle_id ON lessons(vehicle_id);
CREATE INDEX idx_lessons_start_time ON lessons(start_time);
CREATE INDEX idx_student_packages_student_id ON student_packages(student_id);
CREATE INDEX idx_instructor_unavailability_instructor_id ON instructor_unavailability(instructor_id);
CREATE INDEX idx_instructor_unavailability_time_range ON instructor_unavailability(start_time, end_time);

-- Add some sample data
INSERT INTO vehicles (vehicle_type, plate_number, model) VALUES 
('manual', 'ABC123', 'Toyota Vios'),
('automatic', 'XYZ789', 'Honda City'),
('manual', 'DEF456', 'Toyota Corolla');
