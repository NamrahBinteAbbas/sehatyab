from flask import Blueprint, request, jsonify
from database import execute_query, execute_insert
from utils.auth import token_required, role_required
from datetime import datetime, timedelta

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/profile', methods=['GET'])
@token_required
@role_required('Doctor')
def get_profile():
    try:
        user_id = request.user['user_id']
        
        profile = execute_query(
            """SELECT e.*, d.Specialization, d.Qualification, d.RoomID, d.ConsultationFee,
                      r.RoomName, dep.DeptName
               FROM Employee e
               JOIN Doctor d ON e.EmpID = d.EmpID
               LEFT JOIN Room r ON d.RoomID = r.RoomID
               LEFT JOIN Department dep ON e.DeptID = dep.DeptID
               WHERE e.UserID = %s""",
            (user_id,)
        )
        
        if not profile:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        return jsonify(dict(profile[0])), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments', methods=['GET'])
@token_required
@role_required('Doctor')
def get_appointments():
    try:
        user_id = request.user['user_id']
        date = request.args.get('date')
        
        doctor = execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s",
            (user_id,)
        )
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        doctor_id = doctor[0]['empid']
        
        query = """
            SELECT a.*, p.Name as PatientName, p.Age, p.Gender, p.ContactNo,
                   p.BloodGroup, p.Address
            FROM Appointment a
            JOIN Patient p ON a.PatientID = p.PatientID
            WHERE a.DoctorID = %s
        """
        params = [doctor_id]
        
        if date:
            query += " AND DATE(a.AppointmentDateTime) = %s"
            params.append(date)
        else:
            query += " AND DATE(a.AppointmentDateTime) >= CURRENT_DATE"
        
        query += " ORDER BY a.AppointmentDateTime"
        
        appointments = execute_query(query, tuple(params))
        return jsonify([dict(a) for a in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/weekly', methods=['GET'])
@token_required
@role_required('Doctor')
def get_weekly_schedule():
    try:
        user_id = request.user['user_id']
        
        doctor = execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s",
            (user_id,)
        )
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        doctor_id = doctor[0]['empid']
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        appointments = execute_query(
            """SELECT a.*, p.Name as PatientName, p.Age, p.Gender, p.ContactNo
               FROM Appointment a
               JOIN Patient p ON a.PatientID = p.PatientID
               WHERE a.DoctorID = %s
                 AND DATE(a.AppointmentDateTime) BETWEEN %s AND %s
               ORDER BY a.AppointmentDateTime""",
            (doctor_id, week_start, week_end)
        )
        
        return jsonify([dict(a) for a in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/appointments/<int:appointment_id>/prescription', methods=['PUT'])
@token_required
@role_required('Doctor')
def write_prescription(appointment_id):
    try:
        data = request.json
        prescription_text = data.get('prescription_text')
        
        if not prescription_text:
            return jsonify({'error': 'Prescription text is required'}), 400
        
        user_id = request.user['user_id']
        
        doctor = execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s",
            (user_id,)
        )
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        doctor_id = doctor[0]['empid']
        
        appointment = execute_query(
            "SELECT * FROM Appointment WHERE AppointmentID = %s AND DoctorID = %s",
            (appointment_id, doctor_id)
        )
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        execute_query(
            """UPDATE Appointment SET PrescriptionText = %s, Status = 'Completed', UpdatedAt = %s
               WHERE AppointmentID = %s""",
            (prescription_text, datetime.now(), appointment_id),
            fetch=False
        )
        
        return jsonify({'message': 'Prescription added successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['GET'])
@token_required
@role_required('Doctor')
def get_availability():
    try:
        user_id = request.user['user_id']
        
        doctor = execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s",
            (user_id,)
        )
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        doctor_id = doctor[0]['empid']
        
        availability = execute_query(
            """SELECT * FROM DoctorAvailability
               WHERE DoctorID = %s AND AvailableDate >= CURRENT_DATE
               ORDER BY AvailableDate""",
            (doctor_id,)
        )
        
        return jsonify([dict(a) for a in availability]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctor_bp.route('/availability', methods=['POST'])
@token_required
@role_required('Doctor')
def add_availability():
    try:
        data = request.json
        user_id = request.user['user_id']
        
        doctor = execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s",
            (user_id,)
        )
        
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        doctor_id = doctor[0]['empid']
        available_date = data.get('available_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if not all([available_date, start_time, end_time]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = execute_insert(
            """INSERT INTO DoctorAvailability (DoctorID, AvailableDate, StartTime, EndTime)
               VALUES (%s, %s, %s, %s) RETURNING AvailabilityID""",
            (doctor_id, available_date, start_time, end_time)
        )
        
        return jsonify({
            'message': 'Availability added successfully',
            'availability_id': result['availabilityid']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
