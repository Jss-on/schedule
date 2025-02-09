from typing import List, Optional
from app.db.connection import Database

class VehicleService:
    def __init__(self, db: Database):
        self.db = db

    def create_vehicle(self, vehicle_data: dict) -> dict:
        """Create a new vehicle."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO vehicles (
                    vehicle_type, plate_number, model, is_active
                ) VALUES (
                    %(vehicle_type)s, %(plate_number)s, %(model)s, %(is_active)s
                ) RETURNING *
            """, vehicle_data)
            return cur.fetchone()

    def get_vehicle(self, vehicle_id: int) -> Optional[dict]:
        """Get vehicle by ID."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM vehicles WHERE id = %(id)s
            """, {'id': vehicle_id})
            return cur.fetchone()

    def list_vehicles(self) -> List[dict]:
        """List all active vehicles."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM vehicles 
                WHERE is_active = true
                ORDER BY vehicle_type, model
            """)
            return cur.fetchall()

    def update_vehicle(self, vehicle_id: int, vehicle_data: dict) -> Optional[dict]:
        """Update vehicle details."""
        vehicle_data['id'] = vehicle_id
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE vehicles SET
                    vehicle_type = %(vehicle_type)s,
                    plate_number = %(plate_number)s,
                    model = %(model)s,
                    is_active = %(is_active)s
                WHERE id = %(id)s
                RETURNING *
            """, vehicle_data)
            return cur.fetchone()

    def delete_vehicle(self, vehicle_id: int) -> bool:
        """Soft delete a vehicle by setting is_active to false."""
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE vehicles SET is_active = false
                WHERE id = %(id)s
                RETURNING id
            """, {'id': vehicle_id})
            return cur.fetchone() is not None
