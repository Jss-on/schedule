import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to decode JWT token
const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Effect to decode token and set user info on mount or token change
  useEffect(() => {
    if (token) {
      try {
        const decoded = decodeToken(token);
        console.log('Decoded token:', decoded); // Debug log
        if (decoded) {
          setUser({
            email: decoded.sub,
            role: decoded.role,
          });
          console.log('User role set to:', decoded.role); // Debug log
          setIsAuthenticated(true);
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
          throw new Error('Invalid token');
        }
      } catch (error) {
        console.error('Token decode error:', error);
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
      }
    } else {
      setUser(null);
      setIsAuthenticated(false);
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      });

      if (response.data && response.data.access_token) {
        const { access_token } = response.data;
        const decoded = decodeToken(access_token);
        
        if (!decoded) {
          throw new Error('Invalid token received');
        }

        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser({
          email: decoded.sub,
          role: decoded.role,
        });
        setIsAuthenticated(true);
        
        // Set the default Authorization header for future requests
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    delete api.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
