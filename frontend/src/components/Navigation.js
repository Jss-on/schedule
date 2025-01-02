import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="nav">
      <ul className="nav-list">
        <li className="nav-item">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
        </li>
        <li className="nav-item">
          <Link
            to="/appointments"
            className={`nav-link ${
              location.pathname === '/appointments' ? 'active' : ''
            }`}
          >
            Appointments
          </Link>
        </li>
        <li className="nav-item">
          <Link
            to="/instructors"
            className={`nav-link ${
              location.pathname === '/instructors' ? 'active' : ''
            }`}
          >
            Instructors
          </Link>
        </li>
        <li className="nav-item">
          <Link
            to="/vehicles"
            className={`nav-link ${
              location.pathname === '/vehicles' ? 'active' : ''
            }`}
          >
            Vehicles
          </Link>
        </li>
        {user?.role === 'admin' && (
          <li className="nav-item">
            <Link
              to="/coordinators"
              className={`nav-link ${
                location.pathname === '/coordinators' ? 'active' : ''
              }`}
            >
              Coordinators
            </Link>
          </li>
        )}
        <li className="nav-item">
          <button onClick={handleLogout} className="btn-secondary">
            Logout
          </button>
        </li>
      </ul>
    </nav>
  );
};

export default Navigation;
