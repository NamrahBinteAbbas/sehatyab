from flask import Blueprint, request, jsonify
from database import execute_query, execute_insert
from utils.auth import token_required, role_required, hash_password
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/departments', methods=['POST'])
@token_required
@role_required('Admin')
def add_department():
    try:
        data = request.json
        dept_name = data.get('dept_name')
        location = data.get('location', '')
        
        if not dept_name:
            return jsonify({'error': 'Department name is required'}), 400
        
        result = execute_insert(
            "INSERT INTO Department (DeptName, Location) VALUES (%s, %s) RETURNING DeptID",
            (dept_name, location)
        )
        
        return jsonify({
            'message': 'Department added successfully',
            'dept_id': result['deptid']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['GET'])
@token_required
@role_required('Admin')
def get_all_departments():
    try:
        departments = execute_query("SELECT * FROM Department ORDER BY DeptName")
        return jsonify([dict(d) for d in departments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/room-types', methods=['POST'])
@token_required
@role_required('Admin')
def add_room_type():
    try:
        data = request.json
        type_name = data.get('type_name')
        max_rooms = data.get('max_rooms', 0)
        beds_per_room = data.get('beds_per_room', 0)
        charges_per_day = data.get('charges_per_day', 0)
        
        if not type_name:
            return jsonify({'error': 'Type name is required'}), 400
        
        result = execute_insert(
            """INSERT INTO RoomType (TypeName, MaxRooms, BedsPerRoom, ChargesPerDay)
               VALUES (%s, %s, %s, %s) RETURNING TypeID""",
            (type_name, max_rooms, beds_per_room, charges_per_day)
        )
        
        return jsonify({
            'message': 'Room type added successfully',
            'type_id': result['typeid']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/room-types', methods=['GET'])
@token_required
@role_required('Admin')
def get_room_types():
    try:
        room_types = execute_query("SELECT * FROM RoomType ORDER BY TypeName")
        return jsonify([dict(rt) for rt in room_types]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/rooms', methods=['POST'])
@token_required
@role_required('Admin')
def add_room():
    try:
        data = request.json
        type_id = data.get('type_id')
        room_name = data.get('room_name')
        
        if not all([type_id, room_name]):
            return jsonify({'error': 'Type ID and room name are required'}), 400
        
        result = execute_insert(
            "INSERT INTO Room (TypeID, RoomName) VALUES (%s, %s) RETURNING RoomID",
            (type_id, room_name)
        )
        
        return jsonify({
            'message': 'Room added successfully',
            'room_id': result['roomid']
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'Maximum rooms limit reached' in error_msg:
            return jsonify({'error': 'Maximum rooms limit reached for this room type'}), 400
        return jsonify({'error': error_msg}), 500

@admin_bp.route('/rooms', methods=['GET'])
@token_required
@role_required('Admin')
def get_rooms():
    try:
        rooms = execute_query(
            """SELECT r.*, rt.TypeName, rt.BedsPerRoom, rt.ChargesPerDay
               FROM Room r
               JOIN RoomType rt ON r.TypeID = rt.TypeID
               ORDER BY rt.TypeName, r.RoomName"""
        )
        return jsonify([dict(r) for r in rooms]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctors', methods=['POST'])
@token_required
@role_required('Admin')
def add_doctor():
    try:
        data = request.json
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        gender = data.get('gender')
        contact = data.get('contact')
        salary = data.get('salary')
        dept_id = data.get('dept_id')
        specialization = data.get('specialization')
        qualification = data.get('qualification')
        room_id = data.get('room_id')
        consultation_fee = data.get('consultation_fee', 1000)
        
        if not all([username, email, password, name, gender, contact, salary, specialization, qualification]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if room_id:
            room_check = execute_query(
                """SELECT rt.BedsPerRoom FROM Room r 
                   JOIN RoomType rt ON r.TypeID = rt.TypeID 
                   WHERE r.RoomID = %s""",
                (room_id,)
            )
            if not room_check:
                return jsonify({'error': 'Room not found'}), 404
            if room_check[0]['bedsperroom'] > 0:
                return jsonify({'error': 'Doctor must be assigned to consultation/diagnostic room only (not a ward)'}), 400
        
        existing = execute_query(
            "SELECT UserID FROM UserAuth WHERE Username = %s OR Email = %s",
            (username, email)
        )
        
        if existing:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        hashed_pwd = hash_password(password)
        
        user_result = execute_insert(
            """INSERT INTO UserAuth (Username, Email, PasswordHash, UserType, IsActive)
               VALUES (%s, %s, %s, 'Doctor', 'Y') RETURNING UserID""",
            (username, email, hashed_pwd)
        )
        
        user_id = user_result['userid']
        
        emp_result = execute_insert(
            """INSERT INTO Employee (UserID, Name, Gender, Role, Contact, Salary, DeptID, IsActive)
               VALUES (%s, %s, %s, 'Doctor', %s, %s, %s, 'Y') RETURNING EmpID""",
            (user_id, name, gender, contact, salary, dept_id)
        )
        
        emp_id = emp_result['empid']
        
        execute_insert(
            """INSERT INTO Doctor (EmpID, Specialization, Qualification, RoomID, ConsultationFee)
               VALUES (%s, %s, %s, %s, %s)""",
            (emp_id, specialization, qualification, room_id, consultation_fee)
        )
        
        return jsonify({
            'message': 'Doctor added successfully',
            'user_id': user_id,
            'emp_id': emp_id
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'must be assigned to a non-bed' in error_msg:
            return jsonify({'error': 'Doctor must be assigned to consultation/diagnostic room only'}), 400
        return jsonify({'error': error_msg}), 500

@admin_bp.route('/employees', methods=['POST'])
@token_required
@role_required('Admin')
def add_employee():
    try:
        data = request.json
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        gender = data.get('gender')
        role = data.get('role')
        contact = data.get('contact')
        salary = data.get('salary')
        dept_id = data.get('dept_id')
        
        if role not in ['Admin', 'Receptionist']:
            return jsonify({'error': 'Invalid role'}), 400
        
        if not all([username, email, password, name, gender, role, contact, salary]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        existing = execute_query(
            "SELECT UserID FROM UserAuth WHERE Username = %s OR Email = %s",
            (username, email)
        )
        
        if existing:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        hashed_pwd = hash_password(password)
        
        user_result = execute_insert(
            """INSERT INTO UserAuth (Username, Email, PasswordHash, UserType, IsActive)
               VALUES (%s, %s, %s, %s, 'Y') RETURNING UserID""",
            (username, email, hashed_pwd, role)
        )
        
        user_id = user_result['userid']
        
        emp_result = execute_insert(
            """INSERT INTO Employee (UserID, Name, Gender, Role, Contact, Salary, DeptID, IsActive)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'Y') RETURNING EmpID""",
            (user_id, name, gender, role, contact, salary, dept_id)
        )
        
        emp_id = emp_result['empid']
        
        if role == 'Admin':
            can_manage_doctors = data.get('can_manage_doctors', True)
            can_manage_rooms = data.get('can_manage_rooms', True)
            can_view_reports = data.get('can_view_reports', True)
            
            execute_insert(
                """INSERT INTO Admin (EmpID, CanManageDoctors, CanManageRooms, CanViewReports)
                   VALUES (%s, %s, %s, %s)""",
                (emp_id, can_manage_doctors, can_manage_rooms, can_view_reports)
            )
        
        return jsonify({
            'message': 'Employee added successfully',
            'user_id': user_id,
            'emp_id': emp_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/appointments', methods=['GET'])
@token_required
@role_required('Admin')
def get_all_appointments():
    try:
        appointments = execute_query(
            """SELECT a.*, 
                      p.Name as PatientName, p.ContactNo as PatientContact,
                      e.Name as DoctorName, d.Specialization,
                      r.RoomName, dep.DeptName
               FROM Appointment a
               JOIN Patient p ON a.PatientID = p.PatientID
               JOIN Doctor d ON a.DoctorID = d.EmpID
               JOIN Employee e ON d.EmpID = e.EmpID
               LEFT JOIN Room r ON d.RoomID = r.RoomID
               LEFT JOIN Department dep ON e.DeptID = dep.DeptID
               ORDER BY a.AppointmentDateTime DESC"""
        )
        
        return jsonify([dict(a) for a in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/patients', methods=['GET'])
@token_required
@role_required('Admin')
def get_all_patients():
    try:
        patients = execute_query(
            """SELECT p.*, u.Username, u.Email
               FROM Patient p
               LEFT JOIN UserAuth u ON p.UserID = u.UserID
               WHERE p.IsActive = 'Y'
               ORDER BY p.Name"""
        )
        
        return jsonify([dict(p) for p in patients]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bills', methods=['GET'])
@token_required
@role_required('Admin')
def get_all_bills():
    try:
        bills = execute_query(
            """SELECT b.*, 
                      a.AppointmentDateTime,
                      p.Name as PatientName, p.ContactNo,
                      e.Name as DoctorName
               FROM Bill b
               LEFT JOIN Appointment a ON b.AppointmentID = a.AppointmentID
               LEFT JOIN Patient p ON a.PatientID = p.PatientID
               LEFT JOIN Doctor d ON a.DoctorID = d.EmpID
               LEFT JOIN Employee e ON d.EmpID = e.EmpID
               ORDER BY b.BillDate DESC"""
        )
        
        return jsonify([dict(b) for b in bills]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bills/generate', methods=['POST'])
@token_required
@role_required('Admin')
def generate_bill():
    try:
        data = request.json
        appointment_id = data.get('appointment_id')
        admission_id = data.get('admission_id')
        amount = data.get('amount')
        
        if not amount or (not appointment_id and not admission_id):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = execute_insert(
            """INSERT INTO Bill (AppointmentID, AdmissionID, Amount, BillDate, PaymentStatus)
               VALUES (%s, %s, %s, CURRENT_DATE, 'Unpaid') RETURNING BillID""",
            (appointment_id, admission_id, amount)
        )
        
        return jsonify({
            'message': 'Bill generated successfully',
            'bill_id': result['billid']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/doctor-availability', methods=['POST'])
@token_required
@role_required('Admin')
def add_doctor_availability():
    try:
        data = request.json
        doctor_id = data.get('doctor_id')
        available_date = data.get('available_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if not all([doctor_id, available_date, start_time, end_time]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400
        
        existing = execute_query(
            "SELECT AvailabilityID FROM DoctorAvailability WHERE DoctorID = %s AND AvailableDate = %s",
            (doctor_id, available_date)
        )
        
        if existing:
            return jsonify({'error': 'Doctor already has availability set for this date'}), 409
        
        result = execute_insert(
            """INSERT INTO DoctorAvailability (DoctorID, AvailableDate, StartTime, EndTime)
               VALUES (%s, %s, %s, %s) RETURNING AvailabilityID""",
            (doctor_id, available_date, start_time, end_time)
        )
        
        return jsonify({
            'message': 'Doctor availability added successfully',
            'availability_id': result['availabilityid']
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'duplicate key value' in error_msg or 'unique constraint' in error_msg:
            return jsonify({'error': 'Doctor already has availability for this date'}), 409
        return jsonify({'error': error_msg}), 500
