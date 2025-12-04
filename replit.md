# Sehatyaab Hospital Management System

## Project Overview
Full-stack Hospital Management System with Flask (Python) backend and React frontend. Connected to Supabase PostgreSQL database.

## Application Name
**Sehatyaab** - Hospital Management System

## Technology Stack
### Backend
- Flask 3.0.0
- PostgreSQL (Supabase)
- psycopg2-binary 2.9.9
- PyJWT 2.8.0
- bcrypt 4.1.2
- Flask-CORS 4.0.0

### Frontend
- React 18
- Vite 7
- Material-UI (@mui/material)
- React Router DOM
- Axios

## Architecture
### Backend (Port 8080)
- `/api/auth` - Authentication routes (login, register)
- `/api/patient` - Patient APIs (appointments, bills, doctors)
- `/api/admin` - Admin APIs (manage doctors, rooms, appointments, bills)
- `/api/doctor` - Doctor APIs (schedule, appointments, prescriptions)

### Frontend (Port 5000)
- Vite dev server with proxy to backend
- Material-UI components
- Role-based routing (Patient, Admin, Doctor)

## Database
- **Provider**: Supabase PostgreSQL
- **Schema**: Complete hospital management schema with triggers and constraints
- **Features**: 
  - Soft deletes (IsActive='N')
  - Business rules enforcement via triggers
  - 5 appointments/day/doctor limit
  - 30-minute buffer between appointments
  - 1 active appointment/day per patient

## User Roles

### Patient
- Register with full profile (age, gender, blood group, etc.)
- View departments and doctors
- Book/cancel/reschedule appointments
- View appointment history
- View and pay bills (PKR currency)

### Admin
- Add doctors (full Employee + Doctor data)
- Manage departments and rooms
- View all appointments, bills, and patients
- Generate bills
- Add doctor availability

### Doctor
- View weekly schedule
- View appointments with patient details
- Write prescriptions
- Manage availability

## Key Features
- **JWT Authentication**: Secure token-based auth
- **Role-Based Access Control**: Separate dashboards for each user type
- **Business Rules**: 
  - Maximum 5 appointments per doctor per day
  - 30-minute buffer between appointments
  - Patient can only have 1 active appointment per day
  - Doctors assigned to consultation rooms only (no ward rooms)
- **Currency**: All prices in PKR (Pakistani Rupees)
- **Soft Delete**: No record deletion, uses IsActive flag
- **Consultation Fee**: Default Rs. 1000

## Project Structure
```
/backend
  /routes
    - auth_routes.py
    - patient_routes.py
    - admin_routes.py
    - doctor_routes.py
  /utils
    - auth.py (JWT helpers)
  - app.py (Flask app)
  - database.py (DB connection)
  - config.py (Configuration)
  - requirements.txt

/frontend
  /src
    /components
      /Auth (Login, Register)
      /Patient (Dashboard, BookAppointment, ViewAppointments, ViewBills)
      /Admin (Dashboard, AddDoctor, ManageRooms, ViewAll*)
      /Doctor (Dashboard, ViewSchedule, ManageAppointments)
    /services
      - api.js (Axios API calls)
    - App.jsx
```

## Environment Variables (Secrets)
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `SUPABASE_DB_HOST`: Supabase database host
- `SUPABASE_DB_PASSWORD`: Supabase database password

## Running the Application
The application runs automatically via the "Start Application" workflow which:
1. Starts Flask backend on port 8080
2. Starts Vite frontend on port 5000 (proxies /api to backend)

## Recent Changes
- Initial project setup (Dec 4, 2025)
- Complete backend API implementation
- Full frontend with Material-UI
- Role-based dashboards for all user types
- Database integration with Supabase PostgreSQL

## Notes
- Default consultation fee: Rs. 1000
- All patient registration requires complete profile data
- Doctors can only be added by admin
- Admin accounts must be created by existing admin
