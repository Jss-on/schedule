import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const AppointmentForm = ({ appointment, onSubmit, onClose }) => {
  const { token } = useAuth();
  const [instructors, setInstructors] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [formData, setFormData] = useState({
    start_time: '',
    end_time: '',
    student_name: '',
    student_email: '',
    student_phone: '',
    special_requirements: '',
    instructor_id: '',
    vehicle_id: '',
  });

  useEffect(() => {
    if (appointment) {
      setFormData({
        start_time: appointment.start_time.slice(0, 16),
        end_time: appointment.end_time.slice(0, 16),
        student_name: appointment.student_name,
        student_email: appointment.student_email,
        student_phone: appointment.student_phone,
        special_requirements: appointment.special_requirements || '',
        instructor_id: appointment.instructor_id,
        vehicle_id: appointment.vehicle_id,
      });
    }
    fetchInstructors();
    fetchVehicles();
  }, [appointment]);

  const fetchInstructors = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/instructors', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setInstructors(response.data);
    } catch (error) {
      console.error('Error fetching instructors:', error);
    }
  };

  const fetchVehicles = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/vehicles', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setVehicles(response.data);
    } catch (error) {
      console.error('Error fetching vehicles:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>{appointment ? 'Edit Appointment' : 'New Appointment'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Start Time</label>
            <input
              type="datetime-local"
              name="start_time"
              value={formData.start_time}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>End Time</label>
            <input
              type="datetime-local"
              name="end_time"
              value={formData.end_time}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Student Name</label>
            <input
              type="text"
              name="student_name"
              value={formData.student_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Student Email</label>
            <input
              type="email"
              name="student_email"
              value={formData.student_email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Student Phone</label>
            <input
              type="tel"
              name="student_phone"
              value={formData.student_phone}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Special Requirements</label>
            <textarea
              name="special_requirements"
              value={formData.special_requirements}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Instructor</label>
            <select
              name="instructor_id"
              value={formData.instructor_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Instructor</option>
              {instructors.map((instructor) => (
                <option key={instructor.id} value={instructor.id}>
                  {instructor.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Vehicle</label>
            <select
              name="vehicle_id"
              value={formData.vehicle_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Vehicle</option>
              {vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.model} - {vehicle.plate_number}
                </option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              {appointment ? 'Update' : 'Create'}
            </button>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AppointmentForm;
