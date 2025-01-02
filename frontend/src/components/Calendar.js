import React, { useState } from 'react';

const Calendar = ({ appointments }) => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
    });
  };

  const renderHeader = () => {
    return (
      <div className="calendar-header">
        <button
          onClick={() =>
            setCurrentDate(
              new Date(currentDate.getFullYear(), currentDate.getMonth() - 1)
            )
          }
          className="btn-secondary"
        >
          Previous
        </button>
        <h2>{formatDate(currentDate)}</h2>
        <button
          onClick={() =>
            setCurrentDate(
              new Date(currentDate.getFullYear(), currentDate.getMonth() + 1)
            )
          }
          className="btn-secondary"
        >
          Next
        </button>
      </div>
    );
  };

  const renderDays = () => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days.map((day) => (
      <div key={day} className="calendar-cell calendar-header">
        {day}
      </div>
    ));
  };

  const renderCells = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDayOfMonth = getFirstDayOfMonth(currentDate);
    const cells = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
      cells.push(<div key={`empty-${i}`} className="calendar-cell empty"></div>);
    }

    // Add cells for each day of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        day
      );
      const isToday =
        date.toDateString() === new Date().toDateString();

      // Filter appointments for this day
      const dayAppointments = appointments.filter((appointment) => {
        const appointmentDate = new Date(appointment.start_time);
        return appointmentDate.toDateString() === date.toDateString();
      });

      cells.push(
        <div
          key={day}
          className={`calendar-cell ${isToday ? 'today' : ''}`}
        >
          <div className="calendar-day">{day}</div>
          <div className="calendar-appointments">
            {dayAppointments.map((appointment) => (
              <div key={appointment.id} className="calendar-appointment">
                {new Date(appointment.start_time).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
                - {appointment.student_name}
              </div>
            ))}
          </div>
        </div>
      );
    }

    return cells;
  };

  return (
    <div className="calendar">
      {renderHeader()}
      <div className="calendar-grid">
        {renderDays()}
        {renderCells()}
      </div>
    </div>
  );
};

export default Calendar;
