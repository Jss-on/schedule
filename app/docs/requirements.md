# Driving School Scheduling System Requirements

## 1. Course Management
### Lesson Packages
- System must support creation and management of different driving lesson packages
- Each package must specify:
  - Total number of required hours
  - Vehicle type (manual/automatic)
  - Price
  - Package name/tier identifier

### Student Progress Tracking
- System must track remaining hours for each student
- Display completion percentage for each enrolled package
- Maintain history of completed lessons

## 2. User Management
### Student Features
- Students can view their enrolled package details
- Students can view their scheduled lessons
- Students can request cancellation of specific lessons
- Students can view their remaining hours

### Instructor Features
- Instructors can view their assigned lessons
- System must track instructor qualifications (manual/automatic vehicles)

### Admin Features
- Admins can create and modify lesson packages
- Admins can enroll students in packages
- Admins can assign instructors to lessons
- Admins can view system-wide schedule
- Admins can create and manage instructor accounts including:
  - Adding new instructors to the system
  - Setting instructor qualifications (manual/automatic)
  - Managing instructor personal information
  - Deactivating instructor accounts when needed
- Admins can manage student accounts
- Admins can set and modify instructor weekly availability schedules
- Admins can mark instructors as unavailable for specific dates/times

## 3. Scheduling System
### Time Slot Management
- Standard lesson duration is configurable (e.g., 3 hours)
- System must prevent double-booking of instructors
- System must prevent scheduling outside of instructor availability
- System must track vehicle availability

### Schedule Views
- Calendar view showing all scheduled lessons
- Available time slots view
- Instructor availability view
- Vehicle availability view

## 4. Business Rules
- Students cannot be scheduled for more hours than their package includes
- Lessons cannot be scheduled without an available instructor and vehicle
- Cancellation policies must be enforced (time limits, penalties if applicable)
- System must maintain minimum rest periods between instructor assignments

## 5. Reporting
- Daily schedule reports
- Student progress reports
- Instructor utilization reports
- Package enrollment reports

## Future Considerations
- Payment processing integration
- Mobile app for students and instructors
- SMS/Email notifications for schedule changes
- Student evaluation and feedback system
- Digital attendance tracking
