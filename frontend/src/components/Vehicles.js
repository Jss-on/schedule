import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const Vehicles = () => {
  const { token } = useAuth();
  const [vehicles, setVehicles] = useState([]);

  useEffect(() => {
    fetchVehicles();
  }, []);

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

  return (
    <div className="vehicles">
      <div className="vehicles-header">
        <h1>Vehicles</h1>
        <button className="btn-primary">Add Vehicle</button>
      </div>

      <div className="vehicles-list">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Plate Number</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map((vehicle) => (
              <tr key={vehicle.id}>
                <td>{vehicle.model}</td>
                <td>{vehicle.plate_number}</td>
                <td>{vehicle.status}</td>
                <td>
                  <button className="btn-secondary">Edit</button>
                  <button className="btn-danger">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Vehicles;
