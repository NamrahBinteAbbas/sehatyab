from flask import Blueprint, request, jsonify
from database import execute_query, execute_insert
from utils.auth import token_required, role_required
from datetime import datetime

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/departments', methods=['GET'])
@token_required
def get_departments():
    try:
        departments = execute_query("SELECT * FROM Department ORDER BY DeptName")
        return jsonify([dict(d) for d in departments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/doctors', methods=['GET'])
@token_required
def get_doctors():
    try:
        dept_id = request.args.get('dept_id')
        
        query = """
            SELECT e.EmpID, e.Name, e.Gender, e.Contact, e.DeptID,
                   d.Specialization, d.Qualification, d.ConsultationFee, d.RoomID,
                   dep.DeptName, r.RoomName
            FROM Employee e
            JOIN Doctor d ON e.EmpID = d.EmpID
            LEFT JOIN Department dep ON e.DeptID = dep.DeptID
            LEFT JOIN Room r ON d.RoomID = r.RoomID
            WHERE e.IsActive = 'Y'
        """
        params = []
        
        if dept_id:
            query += " AND e.DeptID = %s"
            params.append(dept_id)
        
        query += " ORDER BY e.Name"
        
        doctors = execute_query(query, tuple(params) if params else None)
        return jsonify([dict(d) for d in doctors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/doctor/<int:doctor_id>/availability', methods=['GET'])
@token_required
def get_doctor_availability(doctor_id):
    try:
        date = request.args.get('date')
        
        query = "SELECT * FROM DoctorAvailability WHERE DoctorID = %s"
        params = [doctor_id]
        
        if date:
            query += " AND AvailableDate = %s"
            params.append(date)
        else:
            query += " AND AvailableDate >= CURRENT_DATE"
        
        query += " ORDER BY AvailableDate"
        
        availability = execute_query(query, tuple(params))
        return jsonify([dict(a) for a in availability]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/book', methods=['POST'])
@token_required
@role_required('Patient')
def book_appointment():
    try:
        data = request.json
        user_id = request.user['user_id']
        
        patient = execute_query("SELECT PatientID FROM Patient WHERE UserID = %s", (user_id,))
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        patient_id = patient[0]['patientid']
        doctor_id = data.get('doctor_id')
        appointment_datetime = data.get('appointment_datetime')
        
        if not all([doctor_id, appointment_datetime]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = execute_insert(
            """INSERT INTO Appointment (AppointmentDateTime, Status, DoctorID, PatientID)
               VALUES (%s, 'Scheduled', %s, %s) RETURNING AppointmentID, AppointmentDateTime, Status""",
            (appointment_datetime, doctor_id, patient_id)
        )
        
        doctor_info = execute_query(
            "SELECT ConsultationFee FROM Doctor WHERE EmpID = %s",
            (doctor_id,)
        )
        
        if doctor_info:
            fee = doctor_info[0]['consultationfee']
            execute_insert(
                """INSERT INTO Bill (AppointmentID, Amount, BillDate, PaymentStatus)
                   VALUES (%s, %s, CURRENT_DATE, 'Unpaid')""",
                (result['appointmentid'], fee)
            )
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': dict(result)
        }), 201
        
    except Exception as e:
        error_msg = str(e)
        if 'already has 5 scheduled appointments' in error_msg:
            return jsonify({'error': 'Doctor has reached daily appointment limit (5)'}), 400
        elif 'already has an active appointment' in error_msg:
            return jsonify({'error': 'You already have an appointment on this date'}), 400
        elif 'not available at this appointment datetime' in error_msg:
            return jsonify({'error': 'Doctor is not available at this time'}), 400
        elif 'conflicts with another appointment' in error_msg:
            return jsonify({'error': 'Time slot unavailable (30-minute buffer required)'}), 400
        return jsonify({'error': error_msg}), 500

@patient_bp.route('/appointments', methods=['GET'])
@token_required
@role_required('Patient')
def get_appointments():
    try:
        user_id = request.user['user_id']
        
        patient = execute_query("SELECT PatientID FROM Patient WHERE UserID = %s", (user_id,))
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        patient_id = patient[0]['patientid']
        
        appointments = execute_query(
            """SELECT a.*, e.Name as DoctorName, d.Specialization, r.RoomName,
                      dep.DeptName
               FROM Appointment a
               JOIN Doctor d ON a.DoctorID = d.EmpID
               JOIN Employee e ON d.EmpID = e.EmpID
               LEFT JOIN Room r ON d.RoomID = r.RoomID
               LEFT JOIN Department dep ON e.DeptID = dep.DeptID
               WHERE a.PatientID = %s
               ORDER BY a.AppointmentDateTime DESC""",
            (patient_id,)
        )
        
        return jsonify([dict(a) for a in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@token_required
@role_required('Patient')
def cancel_appointment(appointment_id):
    try:
        user_id = request.user['user_id']
        
        patient = execute_query("SELECT PatientID FROM Patient WHERE UserID = %s", (user_id,))
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        patient_id = patient[0]['patientid']
        
        appointment = execute_query(
            "SELECT * FROM Appointment WHERE AppointmentID = %s AND PatientID = %s",
            (appointment_id, patient_id)
        )
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        if appointment[0]['status'] == 'Cancelled':
            return jsonify({'error': 'Appointment already cancelled'}), 400
        
        execute_query(
            "UPDATE Appointment SET Status = 'Cancelled', UpdatedAt = %s WHERE AppointmentID = %s",
            (datetime.now(), appointment_id),
            fetch=False
        )
        
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
@token_required
@role_required('Patient')
def reschedule_appointment(appointment_id):
    try:
        data = request.json
        user_id = request.user['user_id']
        new_datetime = data.get('new_datetime')
        
        if not new_datetime:
            return jsonify({'error': 'New datetime is required'}), 400
        
        patient = execute_query("SELECT PatientID FROM Patient WHERE UserID = %s", (user_id,))
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        patient_id = patient[0]['patientid']
        
        appointment = execute_query(
            "SELECT * FROM Appointment WHERE AppointmentID = %s AND PatientID = %s",
            (appointment_id, patient_id)
        )
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        if appointment[0]['status'] == 'Cancelled':
            return jsonify({'error': 'Cannot reschedule cancelled appointment'}), 400
        
        execute_query(
            "UPDATE Appointment SET AppointmentDateTime = %s WHERE AppointmentID = %s",
            (new_datetime, appointment_id),
            fetch=False
        )
        
        updated = execute_query(
            "SELECT Status, RescheduleCount FROM Appointment WHERE AppointmentID = %s",
            (appointment_id,)
        )
        
        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'status': updated[0]['status'] if updated else 'Rescheduled',
            'reschedule_count': updated[0]['reschedulecount'] if updated else None
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        if 'already has 5 scheduled appointments' in error_msg:
            return jsonify({'error': 'Doctor has reached daily appointment limit (5)'}), 400
        elif 'already has an active appointment' in error_msg:
            return jsonify({'error': 'You already have an appointment on this date'}), 400
        elif 'not available at this appointment datetime' in error_msg:
            return jsonify({'error': 'Doctor is not available at this time'}), 400
        elif 'conflicts with another appointment' in error_msg:
            return jsonify({'error': 'Time slot unavailable (30-minute buffer required)'}), 400
        return jsonify({'error': error_msg}), 500

@patient_bp.route('/bills', methods=['GET'])
@token_required
@role_required('Patient')
def get_bills():
    try:
        user_id = request.user['user_id']
        
        patient = execute_query("SELECT PatientID FROM Patient WHERE UserID = %s", (user_id,))
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        patient_id = patient[0]['patientid']
        
        bills = execute_query(
            """SELECT b.*, a.AppointmentDateTime, e.Name as DoctorName, d.Specialization
               FROM Bill b
               LEFT JOIN Appointment a ON b.AppointmentID = a.AppointmentID
               LEFT JOIN Doctor d ON a.DoctorID = d.EmpID
               LEFT JOIN Employee e ON d.EmpID = e.EmpID
               WHERE (a.PatientID = %s OR b.AdmissionID IN 
                     (SELECT AdmissionID FROM Admission WHERE PatientID = %s))
               ORDER BY b.BillDate DESC""",
            (patient_id, patient_id)
        )
        
        return jsonify([dict(b) for b in bills]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patient_bp.route('/bills/<int:bill_id>/pay', methods=['PUT'])
@token_required
@role_required('Patient')
def pay_bill(bill_id):
    try:
        data = request.json
        payment_method = data.get('payment_method', 'Cash')
        user_id = request.user['user_id']
        
        if payment_method not in ['Cash', 'Credit Card', 'Debit Card', 'Insurance', 'Online', 'Other']:
            return jsonify({'error': 'Invalid payment method'}), 400
        
        patient = execute_query("SELECT PatientID FROM Patient WHERE UserID = %s", (user_id,))
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        patient_id = patient[0]['patientid']
        
        bill_check = execute_query(
            """SELECT b.BillID, a.PatientID as AppointmentPatient, adm.PatientID as AdmissionPatient
               FROM Bill b
               LEFT JOIN Appointment a ON b.AppointmentID = a.AppointmentID
               LEFT JOIN Admission adm ON b.AdmissionID = adm.AdmissionID
               WHERE b.BillID = %s""",
            (bill_id,)
        )
        
        if not bill_check:
            return jsonify({'error': 'Bill not found'}), 404
        
        bill_data = bill_check[0]
        appt_patient = bill_data['appointmentpatient']
        adm_patient = bill_data['admissionpatient']
        
        owns_bill = (appt_patient == patient_id) or (adm_patient == patient_id)
        
        if not owns_bill:
            return jsonify({'error': 'Access denied: This bill does not belong to you'}), 403
        
        execute_query(
            "UPDATE Bill SET PaymentStatus = 'Paid', PaymentMethod = %s WHERE BillID = %s",
            (payment_method, bill_id),
            fetch=False
        )
        
        return jsonify({'message': 'Bill paid successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
