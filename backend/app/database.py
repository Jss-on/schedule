import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    host = os.getenv("DB_HOST", "db")
    database = os.getenv("DB_NAME", "schedule_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    
    logger.info(f"Connecting to database - host: {host}, database: {database}, user: {user}")
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        cursor_factory=RealDictCursor
    )

@contextmanager
def get_db_cursor():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise e
    finally:
        conn.close()

def create_default_admin():
    from .auth import get_password_hash
    from .models import User
    
    logger.info("Creating default admin user")
    with get_db_cursor() as cursor:
        # Check if admin already exists
        cursor.execute("SELECT * FROM users WHERE email = 'admin@example.com'")
        existing_admin = cursor.fetchone()
        logger.info(f"Existing admin found: {existing_admin is not None}")
        
        if existing_admin is None:
            # Create default admin user
            admin = User.create(
                cursor=cursor,
                email='admin@example.com',
                hashed_password=get_password_hash('admin123'),
                full_name='Admin User',
                role='admin'
            )
            logger.info(f"Created admin user: {admin}")

def init_db():
    """Initialize the database with required tables"""
    logger.info("Starting database initialization")
    with get_db_cursor() as cursor:
        # Drop existing tables and types
        logger.info("Dropping existing tables")
        cursor.execute("""
            DROP TABLE IF EXISTS appointments CASCADE;
            DROP TABLE IF EXISTS vehicles CASCADE;
            DROP TABLE IF EXISTS instructors CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            DROP TYPE IF EXISTS user_role CASCADE;
        """)
        
        # Create enum type if it doesn't exist
        logger.info("Creating user_role enum type")
        cursor.execute("""
            DO $$ BEGIN
                CREATE TYPE user_role AS ENUM ('admin', 'coordinator', 'instructor');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role user_role NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create instructors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instructors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL,
                specialization VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create vehicles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY,
                make VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                year INTEGER NOT NULL,
                plate_number VARCHAR(20) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'available',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                student_name VARCHAR(255) NOT NULL,
                student_email VARCHAR(255) NOT NULL,
                student_phone VARCHAR(20) NOT NULL,
                start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                end_time TIMESTAMP WITH TIME ZONE NOT NULL,
                instructor_id INTEGER REFERENCES instructors(id),
                vehicle_id INTEGER REFERENCES vehicles(id),
                status VARCHAR(20) DEFAULT 'scheduled',
                special_requirements TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verify tables were created
        logger.info("Verifying tables")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        logger.info(f"Created tables: {tables}")
    
    # Create default admin user
    logger.info("Creating default admin user")
    create_default_admin()
    
    # Verify admin user was created
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        logger.info(f"Users in database: {users}")

def drop_db():
    """Drop all tables in the database"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS appointments;
            DROP TABLE IF EXISTS vehicles;
            DROP TABLE IF EXISTS instructors;
            DROP TABLE IF EXISTS users;
            DROP TYPE IF EXISTS user_role;
        """)
