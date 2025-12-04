# Sehatyaab Hospital Management System

A full-stack Hospital Management System with Flask backend and React frontend.

## Features

### Patient Portal
- Register with complete profile (age, gender, blood group, emergency contact)
- View departments and available doctors
- Book appointments with real-time availability checking
- Cancel or reschedule appointments
- View appointment history with prescriptions
- View and pay bills (in PKR)

### Admin Portal
- Add doctors with complete Employee + Doctor data
- Assign doctors to consultation rooms only
- Manage departments and rooms
- View all appointments, bills, and patients
- Generate bills for appointments
- Set doctor availability schedules

### Doctor Portal
- View weekly appointment schedule
- View appointment details with patient information
- Write prescriptions for completed appointments
- Manage personal availability

## Business Rules Implemented
- Maximum 5 appointments per doctor per day
- 30-minute buffer between appointments
- One active appointment per patient per day
- Doctors can only be assigned to consultation/diagnostic rooms (not wards)
- Soft delete only (no record deletion, uses IsActive flag)
- All prices in Pakistani Rupees (PKR)

## Tech Stack

### Backend
- Flask 3.0.0 (Python)
- PostgreSQL (Supabase)
- JWT Authentication
- bcrypt for password hashing
- CORS enabled

### Frontend
- React 18 with Vite
- Material-UI for components
- React Router for navigation
- Axios for HTTP requests

## Setup

### Prerequisites
- Python 3.11
- Node.js 20
- Supabase PostgreSQL database

### Environment Variables
Set these as Replit Secrets:
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `SUPABASE_DB_HOST` - Your Supabase database host
- `SUPABASE_DB_PASSWORD` - Your Supabase database password

### Database Schema
Run the provided SQL schema file to set up all tables, triggers, and constraints. The schema includes:
- UserAuth, Patient, Doctor, Admin, Employee tables
- Department, Room, RoomType management
- Appointment scheduling with business rule triggers
- Bill management
- Soft delete triggers

### Running the Application
The application runs automatically with the "Start Application" workflow:
- Backend runs on port 8080
- Frontend runs on port 5000 (with proxy to backend)

Access the application at the Replit webview URL.

## Default Credentials
Use the test doctor account from the schema:
- Username: `drtest`
- Password: (check the database schema)

Or register as a new patient.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register (Patient only)

### Patient APIs
- `GET /api/patient/departments` - Get all departments
- `GET /api/patient/doctors` - Get all doctors (with optional dept_id filter)
- `GET /api/patient/doctor/:id/availability` - Get doctor availability
- `POST /api/patient/appointments/book` - Book appointment
- `GET /api/patient/appointments` - Get patient's appointments
- `PUT /api/patient/appointments/:id/cancel` - Cancel appointment
- `PUT /api/patient/appointments/:id/reschedule` - Reschedule appointment
- `GET /api/patient/bills` - Get patient's bills
- `PUT /api/patient/bills/:id/pay` - Pay a bill

### Admin APIs
- `POST /api/admin/departments` - Add department
- `GET /api/admin/departments` - Get all departments
- `POST /api/admin/rooms` - Add room
- `GET /api/admin/rooms` - Get all rooms
- `POST /api/admin/room-types` - Add room type
- `GET /api/admin/room-types` - Get all room types
- `POST /api/admin/doctors` - Add doctor
- `POST /api/admin/employees` - Add employee/admin
- `GET /api/admin/appointments` - Get all appointments
- `GET /api/admin/patients` - Get all patients
- `GET /api/admin/bills` - Get all bills
- `POST /api/admin/bills/generate` - Generate bill
- `POST /api/admin/doctor-availability` - Add doctor availability

### Doctor APIs
- `GET /api/doctor/profile` - Get doctor profile
- `GET /api/doctor/appointments` - Get doctor's appointments
- `GET /api/doctor/appointments/weekly` - Get weekly schedule
- `PUT /api/doctor/appointments/:id/prescription` - Write prescription
- `GET /api/doctor/availability` - Get doctor's availability
- `POST /api/doctor/availability` - Add availability

## Currency
All prices are in Pakistani Rupees (PKR). Default consultation fee is Rs. 1000.

## Security
- Passwords are hashed using bcrypt
- JWT tokens for authentication (7-day expiry)
- Role-based access control
- CORS enabled for frontend-backend communication

## Notes
- Admin and Doctor accounts can only be created by existing admins
- Patients can self-register
- All database triggers enforce business rules automatically
- The database prevents record deletion and requires soft deletes (IsActive='N')
