import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const CoordinatorManagement = () => {
  const [coordinators, setCoordinators] = useState([]);
  const [newCoordinator, setNewCoordinator] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'coordinator'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { user } = useAuth();

  console.log('CoordinatorManagement render - user:', user); // Debug log

  useEffect(() => {
    fetchCoordinators();
  }, []);

  const fetchCoordinators = async () => {
    try {
      console.log('Fetching coordinators...'); // Debug log
      const response = await fetch('/api/users/coordinators', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch coordinators');
      }
      
      const data = await response.json();
      console.log('Fetched coordinators:', data); // Debug log
      setCoordinators(data);
    } catch (error) {
      console.error('Error fetching coordinators:', error);
      setError('Failed to fetch coordinators');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const requestData = {
        email: newCoordinator.email,
        password: newCoordinator.password,
        full_name: newCoordinator.full_name
      };

      console.log('Creating coordinator with data:', {
        email: requestData.email,
        full_name: requestData.full_name
      }); // Debug log without password

      const response = await fetch('/api/auth/coordinators', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(requestData),
      });

      let responseData;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.indexOf("application/json") !== -1) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      console.log('Server response:', {
        status: response.status,
        statusText: response.statusText,
        contentType: contentType,
        data: responseData
      });

      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 422) {
          let errorMessage;
          if (typeof responseData === 'string') {
            errorMessage = responseData;
          } else if (Array.isArray(responseData)) {
            errorMessage = responseData[0]?.msg || 'Validation error';
          } else {
            errorMessage = responseData.detail || 'Invalid input';
          }
          throw new Error(errorMessage);
        }
        throw new Error(typeof responseData === 'string' ? responseData : (responseData.detail || 'Failed to create coordinator'));
      }

      console.log('Coordinator created successfully:', responseData);
      
      setSuccess('Coordinator created successfully');
      setNewCoordinator({ 
        email: '', 
        password: '', 
        full_name: '',
        role: 'coordinator' 
      });
      fetchCoordinators();
    } catch (error) {
      console.error('Error creating coordinator:', {
        message: error.message,
        error: error
      });
      setError(typeof error.message === 'string' ? error.message : 'Failed to create coordinator. Please try again.');
    }
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Coordinator Management</h1>
      
      {/* Error Alert */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Success Alert */}
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{success}</span>
        </div>
      )}

      {/* Add Coordinator Form */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Add New Coordinator</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              id="email"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={newCoordinator.email}
              onChange={(e) => setNewCoordinator({ ...newCoordinator, email: e.target.value })}
              required
            />
          </div>

          <div className="mb-4">
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">Full Name</label>
            <input
              type="text"
              id="full_name"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={newCoordinator.full_name}
              onChange={(e) => setNewCoordinator({ ...newCoordinator, full_name: e.target.value })}
              required
            />
          </div>

          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              id="password"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              value={newCoordinator.password}
              onChange={(e) => setNewCoordinator({ ...newCoordinator, password: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Add Coordinator
          </button>
        </form>
      </div>

      {/* Coordinators List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Existing Coordinators</h2>
        {coordinators.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {coordinators.map((coordinator) => (
              <li key={coordinator.email} className="py-4">
                <div className="flex items-center space-x-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {coordinator.email}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No coordinators found.</p>
        )}
      </div>
    </div>
  );
};

export default CoordinatorManagement;
