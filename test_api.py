import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"

def test_api():
    # 1. Create an instructor
    instructor_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "qualifications": ["Class 3", "Class 3A"],
        "weekly_availability": {
            "monday": [
                {"start": "09:00", "end": "12:00"},
                {"start": "14:00", "end": "17:00"}
            ],
            "wednesday": [
                {"start": "09:00", "end": "17:00"}
            ],
            "friday": [
                {"start": "09:00", "end": "17:00"}
            ]
        },
        "is_active": True
    }
    
    print("\n1. Creating instructor...")
    response = requests.post(f"{BASE_URL}/instructors/", json=instructor_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    instructor_id = response.json()["id"]

    # 2. Create a package
    package_data = {
        "name": "Basic Manual Package",
        "hours": 10,
        "vehicle_type": "Manual",
        "price": 800.00,
        "description": "10-hour manual transmission driving course",
        "is_active": True
    }
    
    print("\n2. Creating package...")
    response = requests.post(f"{BASE_URL}/packages/", json=package_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    package_id = response.json()["id"]

    # 3. Create a vehicle
    vehicle_data = {
        "vehicle_type": "Manual",
        "plate_number": "ABC123",
        "model": "Toyota Corolla",
        "is_active": True
    }
    
    print("\n3. Creating vehicle...")
    response = requests.post(f"{BASE_URL}/vehicles/", json=vehicle_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    vehicle_id = response.json()["id"]

    # Create a student
    student_data = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1987654321"
    }
    
    print("\n4. Creating student...")
    response = requests.post(f"{BASE_URL}/students/", json=student_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    student_id = response.json()["id"]

    # Create student package
    student_package_data = {
        "student_id": student_id,
        "package_id": package_id,
        "hours_remaining": 10
    }
    
    print("\n5. Creating student package...")
    response = requests.post(f"{BASE_URL}/student-packages/", json=student_package_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    student_package_id = response.json()["id"]

    # 4. Create a lesson
    lesson_data = {
        "student_id": student_id,
        "instructor_id": instructor_id,
        "vehicle_id": vehicle_id,
        "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00"),
        "duration": 120,  # 2 hours
        "status": "scheduled",
        "notes": "First driving lesson",
        "student_package_id": student_package_id
    }
    
    print("\n6. Creating lesson...")
    response = requests.post(f"{BASE_URL}/lessons/", json=lesson_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_api()
