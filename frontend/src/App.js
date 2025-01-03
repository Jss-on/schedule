import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import AppointmentForm from './components/AppointmentForm';
import Schedule from './components/Schedule';
import InstructorManagement from './components/InstructorManagement';
import VehicleManagement from './components/VehicleManagement';
import CoordinatorManagement from './components/CoordinatorManagement';

const PrivateLayout = ({ children }) => {
  const { isAuthenticated } = useAuth();
  console.log('PrivateLayout - isAuthenticated:', isAuthenticated); // Debug log
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </div>
    </div>
  );
};

const AdminRoute = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  console.log('AdminRoute - user:', user, 'isAuthenticated:', isAuthenticated); // Debug log
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!user || user.role !== 'admin') {
    return <Navigate to="/dashboard" />;
  }

  return <PrivateLayout>{children}</PrivateLayout>;
};

const StaffRoute = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  console.log('StaffRoute - user:', user, 'isAuthenticated:', isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!user || (user.role !== 'admin' && user.role !== 'coordinator')) {
    return <Navigate to="/dashboard" />;
  }

  return <PrivateLayout>{children}</PrivateLayout>;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <PrivateLayout>
                <Dashboard />
              </PrivateLayout>
            }
          />
          <Route
            path="/appointments"
            element={
              <PrivateLayout>
                <AppointmentForm />
              </PrivateLayout>
            }
          />
          <Route
            path="/schedule"
            element={
              <PrivateLayout>
                <Schedule />
              </PrivateLayout>
            }
          />
          <Route
            path="/instructors"
            element={
              <StaffRoute>
                <InstructorManagement />
              </StaffRoute>
            }
          />
          <Route
            path="/vehicles"
            element={
              <StaffRoute>
                <VehicleManagement />
              </StaffRoute>
            }
          />
          <Route
            path="/coordinators"
            element={
              <AdminRoute>
                <CoordinatorManagement />
              </AdminRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
