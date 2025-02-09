from typing import List, Dict, Optional
from app.db.connection import Database
from app.db.queries.packages import (
    CREATE_PACKAGE, GET_PACKAGE, LIST_PACKAGES, UPDATE_PACKAGE,
    CREATE_STUDENT_PACKAGE, GET_STUDENT_PACKAGE, LIST_STUDENT_PACKAGES
)

class PackageService:
    def __init__(self, db: Database):
        self.db = db

    def create_package(self, package_data: dict) -> dict:
        """Create a new lesson package."""
        with self.db.get_cursor() as cur:
            cur.execute(CREATE_PACKAGE, package_data)
            return cur.fetchone()

    def get_package(self, package_id: int) -> Optional[dict]:
        """Get package by ID."""
        with self.db.get_cursor() as cur:
            cur.execute(GET_PACKAGE, {'id': package_id})
            return cur.fetchone()

    def list_packages(self) -> List[dict]:
        """List all active packages."""
        with self.db.get_cursor() as cur:
            cur.execute(LIST_PACKAGES)
            return cur.fetchall()

    def update_package(self, package_id: int, package_data: dict) -> Optional[dict]:
        """Update package details."""
        package_data['id'] = package_id
        with self.db.get_cursor() as cur:
            cur.execute(UPDATE_PACKAGE, package_data)
            return cur.fetchone()

    def deactivate_package(self, package_id: int) -> Optional[dict]:
        """Deactivate a package."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE packages 
                SET is_active = false 
                WHERE id = %(id)s
                RETURNING *
            """, {'id': package_id})
            return cur.fetchone()

    def assign_package_to_student(self, student_id: int, package_id: int) -> dict:
        """Assign a package to a student."""
        with self.db.get_cursor() as cur:
            # Get package hours
            cur.execute("SELECT hours FROM packages WHERE id = %(id)s", {'id': package_id})
            package = cur.fetchone()
            if not package:
                raise ValueError("Package not found")

            # Create student package with full hours
            student_package_data = {
                'student_id': student_id,
                'package_id': package_id,
                'hours_remaining': package['hours']
            }
            cur.execute(CREATE_STUDENT_PACKAGE, student_package_data)
            return cur.fetchone()

    def get_student_package(self, student_package_id: int) -> Optional[dict]:
        """Get student package by ID."""
        with self.db.get_cursor() as cur:
            cur.execute(GET_STUDENT_PACKAGE, {'id': student_package_id})
            return cur.fetchone()

    def list_student_packages(self, student_id: int) -> List[dict]:
        """List all packages assigned to a student."""
        with self.db.get_cursor() as cur:
            cur.execute(LIST_STUDENT_PACKAGES, {'student_id': student_id})
            return cur.fetchall()

    def update_package_hours(self, student_package_id: int, hours_used: float) -> Optional[dict]:
        """Update remaining hours in a student's package."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE student_packages
                SET hours_remaining = hours_remaining - %(hours_used)s
                WHERE id = %(id)s
                RETURNING *
            """, {
                'id': student_package_id,
                'hours_used': hours_used
            })
            return cur.fetchone()
