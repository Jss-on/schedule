import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import AppointmentForm from './AppointmentForm';

const Appointments = () => {
  const { token } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/appointments', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    }
  };

  const handleEdit = (appointment) => {
    setSelectedAppointment(appointment);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this appointment?')) {
      try {
        await axios.delete(`http://localhost:8000/api/appointments/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        fetchAppointments();
      } catch (error) {
        console.error('Error deleting appointment:', error);
      }
    }
  };

  const handleSubmit = async (appointmentData) => {
    try {
      if (selectedAppointment) {
        await axios.put(
          `http://localhost:8000/api/appointments/${selectedAppointment.id}`,
          appointmentData,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
      } else {
        await axios.post(
          'http://localhost:8000/api/appointments',
          appointmentData,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
      }
      fetchAppointments();
      setShowForm(false);
      setSelectedAppointment(null);
    } catch (error) {
      console.error('Error saving appointment:', error);
    }
  };

  return (
    <div className="appointments">
      <div className="appointments-header">
        <h1>Appointments</h1>
        <button onClick={() => setShowForm(true)} className="btn-primary">
          New Appointment
        </button>
      </div>

      <div className="appointments-list">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Student</th>
              <th>Instructor</th>
              <th>Vehicle</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((appointment) => (
              <tr key={appointment.id}>
                <td>{new Date(appointment.start_time).toLocaleDateString()}</td>
                <td>
                  {new Date(appointment.start_time).toLocaleTimeString()} -
                  {new Date(appointment.end_time).toLocaleTimeString()}
                </td>
                <td>{appointment.student_name}</td>
                <td>{appointment.instructor_id}</td>
                <td>{appointment.vehicle_id}</td>
                <td>{appointment.status}</td>
                <td>
                  <button
                    onClick={() => handleEdit(appointment)}
                    className="btn-secondary"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(appointment.id)}
                    className="btn-danger"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <AppointmentForm
          appointment={selectedAppointment}
          onSubmit={handleSubmit}
          onClose={() => {
            setShowForm(false);
            setSelectedAppointment(null);
          }}
        />
      )}
    </div>
  );
};

export default Appointments;
