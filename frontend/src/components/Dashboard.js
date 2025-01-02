import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { CalendarIcon, UserGroupIcon, TruckIcon } from '@heroicons/react/24/outline';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const stats = [
    { name: 'Appointments Today', value: '12', icon: CalendarIcon },
    { name: 'Active Instructors', value: '8', icon: UserGroupIcon },
    { name: 'Available Vehicles', value: '15', icon: TruckIcon },
  ];

  return (
    <div className="min-h-full">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">Scheduling System</h1>
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-gray-700 mr-4">Welcome, {user?.email}</span>
              <button
                onClick={handleLogout}
                className="btn btn-secondary"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats */}
        <div className="mt-8">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            {stats.map((item) => (
              <div key={item.name} className="card">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <item.icon className="h-6 w-6 text-primary-600" aria-hidden="true" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">{item.name}</dt>
                      <dd className="text-3xl font-semibold text-gray-900">{item.value}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main content area */}
        <div className="mt-8">
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {/* Recent Appointments */}
            <div className="card">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Recent Appointments
              </h3>
              <div className="flow-root">
                <ul className="-my-5 divide-y divide-gray-200">
                  <li className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          John Doe - Driving Test
                        </p>
                        <p className="text-sm text-gray-500">
                          Today at 2:00 PM
                        </p>
                      </div>
                      <div>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Confirmed
                        </span>
                      </div>
                    </div>
                  </li>
                  {/* Add more appointments as needed */}
                </ul>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate('/appointments/new')}
                >
                  New Appointment
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => navigate('/schedule')}
                >
                  View Schedule
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => navigate('/instructors')}
                >
                  Manage Instructors
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => navigate('/vehicles')}
                >
                  Manage Vehicles
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
