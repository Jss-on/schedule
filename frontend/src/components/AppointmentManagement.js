import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import AppointmentForm from './AppointmentForm';

const AppointmentManagement = () => {
  const { token } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (formData) => {
    try {
      await axios.post('http://localhost:8000/api/appointments', formData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      navigate('/appointments');
    } catch (error) {
      console.error('Error creating appointment:', error);
      alert('Failed to create appointment. Please try again.');
    }
  };

  const handleClose = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">New Appointment</h2>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-500"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <AppointmentForm
              onSubmit={handleSubmit}
              onClose={handleClose}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppointmentManagement;
