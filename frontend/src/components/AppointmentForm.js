import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

const AppointmentForm = ({ appointment, onSubmit, onClose }) => {
  const { token } = useAuth();
  const [instructors, setInstructors] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [timeSlots, setTimeSlots] = useState([]);
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
      const startDate = new Date(appointment.start_time);
      setSelectedDate(startDate);
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

  useEffect(() => {
    if (selectedDate && formData.instructor_id && formData.vehicle_id) {
      fetchAvailability();
    }
  }, [selectedDate, formData.instructor_id, formData.vehicle_id]);

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

  const fetchAvailability = async () => {
    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      const response = await axios.get('http://localhost:8000/api/availability/check', {
        params: {
          date: dateStr,
          instructor_id: formData.instructor_id,
          vehicle_id: formData.vehicle_id,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      setTimeSlots(response.data);
    } catch (error) {
      console.error('Error fetching availability:', error);
    }
  };

  const checkDateAvailability = async (date) => {
    // Skip check if no instructor or vehicle is selected
    if (!formData.instructor_id && !formData.vehicle_id) {
      return true;
    }

    try {
      const dateStr = date.toISOString().split('T')[0];
      const response = await axios.get('http://localhost:8000/api/availability/check-date', {
        params: {
          date: dateStr,
          ...(formData.instructor_id && { instructor_id: formData.instructor_id }),
          ...(formData.vehicle_id && { vehicle_id: formData.vehicle_id }),
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error) {
      console.error('Error checking date availability:', error);
      return false;
    }
  };

  const handleDateChange = (date) => {
    setSelectedDate(date);
    setFormData(prev => ({
      ...prev,
      start_time: '',
      end_time: '',
    }));
  };

  const handleTimeSlotSelect = (startTime, endTime) => {
    setFormData(prev => ({
      ...prev,
      start_time: startTime,
      end_time: endTime,
    }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Reset selected date when instructor or vehicle changes
    if (name === 'instructor_id' || name === 'vehicle_id') {
      setSelectedDate(null);
      setTimeSlots([]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const renderTimeSlots = () => {
    if (!timeSlots.length) return null;

    return (
      <div className="grid grid-cols-4 gap-2 mt-4">
        {timeSlots.map((slot, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handleTimeSlotSelect(slot.start_time, slot.end_time)}
            disabled={!slot.is_available}
            className={`p-2 text-sm rounded-md ${
              slot.is_available
                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                : 'bg-red-100 text-red-800 cursor-not-allowed'
            } ${
              formData.start_time === slot.start_time
                ? 'ring-2 ring-primary-500'
                : ''
            }`}
          >
            {new Date(slot.start_time).toLocaleTimeString([], { 
              hour: '2-digit',
              minute: '2-digit'
            })}
          </button>
        ))}
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Instructor</label>
          <select
            name="instructor_id"
            value={formData.instructor_id}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="">Select Instructor</option>
            {instructors.map((instructor) => (
              <option key={instructor.id} value={instructor.id}>
                {instructor.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Vehicle</label>
          <select
            name="vehicle_id"
            value={formData.vehicle_id}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          >
            <option value="">Select Vehicle</option>
            {vehicles.map((vehicle) => (
              <option key={vehicle.id} value={vehicle.id}>
                {vehicle.model} - {vehicle.plate_number}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Date</label>
          <DatePicker
            selected={selectedDate}
            onChange={handleDateChange}
            dateFormat="MMMM d, yyyy"
            minDate={new Date()}
            filterDate={checkDateAvailability}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            placeholderText="Select a date"
          />
        </div>

        {selectedDate && formData.instructor_id && formData.vehicle_id && (
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Available Time Slots</label>
            {renderTimeSlots()}
          </div>
        )}

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Student Name</label>
          <input
            type="text"
            name="student_name"
            value={formData.student_name}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Student Email</label>
          <input
            type="email"
            name="student_email"
            value={formData.student_email}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Student Phone</label>
          <input
            type="tel"
            name="student_phone"
            value={formData.student_phone}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Special Requirements</label>
          <textarea
            name="special_requirements"
            value={formData.special_requirements}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            rows="3"
          />
        </div>
      </div>

      <div className="flex justify-end space-x-4 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={!selectedDate || !formData.start_time}
          className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
            ${(!selectedDate || !formData.start_time) 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
            }`}
        >
          {appointment ? 'Update' : 'Create'}
        </button>
      </div>
    </form>
  );
};

export default AppointmentForm;
