from flask import Blueprint, request, jsonify
from database import execute_query, execute_insert
from utils.auth import token_required, role_required
from datetime import datetime
from typing import Any, List, Optional
from psycopg2.extras import RealDictRow

patient_bp = Blueprint('patient', __name__)


def get_user_id() -> int:
    """Helper to safely extract user_id from request"""
    user_data = getattr(request, 'user', None)
    if not user_data or not isinstance(user_data, dict):
        raise ValueError("User authentication data not found")
    user_id = user_data.get('user_id')
    if not isinstance(user_id, int):
        raise ValueError("Invalid user ID")
    return user_id


def safe_execute_query(query: str, params: tuple) -> List[RealDictRow]:
    """Execute query and ensure it returns a list"""
    result = execute_query(query, params)
    if isinstance(result, list):
        return result
    return []


@patient_bp.route('/departments', methods=['GET'])
@token_required
def get_departments():
    """Get all departments"""
    try:
        departments = safe_execute_query(
            "SELECT * FROM Department ORDER BY DeptName", ())
        return jsonify([dict(d) for d in departments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/doctors', methods=['GET'])
@token_required
def get_doctors():
    """Get doctors (optionally filtered by department)"""
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
        params: List[Any] = []

        if dept_id:
            query += " AND e.DeptID = %s"
            params.append(dept_id)

        query += " ORDER BY e.Name"

        doctors = safe_execute_query(query, tuple(params))
        return jsonify([dict(d) for d in doctors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/doctor/<int:doctor_id>/availability', methods=['GET'])
@token_required
def get_doctor_availability(doctor_id: int):
    """Get doctor's availability (optionally filtered by date)"""
    try:
        date = request.args.get('date')

        query = "SELECT * FROM DoctorAvailability WHERE DoctorID = %s"
        params: List[Any] = [doctor_id]

        if date:
            query += " AND AvailableDate = %s"
            params.append(date)
        else:
            query += " AND AvailableDate >= CURRENT_DATE"

        query += " ORDER BY AvailableDate"

        availability = safe_execute_query(query, tuple(params))
        return jsonify([dict(a) for a in availability]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/appointments/book', methods=['POST'])
@token_required
@role_required('Patient')
def book_appointment():
    """Book a new appointment"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        user_id = get_user_id()

        # Get patient ID
        patient = safe_execute_query(
            "SELECT PatientID FROM Patient WHERE UserID = %s", (user_id, ))

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        patient_id: int = int(patient[0]['patientid'])
        doctor_id = data.get('doctor_id')
        appointment_datetime_str = data.get('appointment_datetime')

        if not all([doctor_id, appointment_datetime_str]):
            return jsonify({
                'error':
                'Missing required fields: doctor_id, appointment_datetime'
            }), 400

        # Parse datetime - PostgreSQL will treat as PKT since DB timezone is set
        try:
            # Remove any timezone info and parse as naive datetime
            if isinstance(appointment_datetime_str, str):
                # Handle various formats: "2025-12-07T01:00:00" or "2025-12-07T01:00:00+05:00"
                clean_dt_str = appointment_datetime_str.split('+')[0].split(
                    'Z')[0]
                appointment_datetime = datetime.fromisoformat(clean_dt_str)
            else:
                raise ValueError("appointment_datetime must be a string")
        except (ValueError, AttributeError) as e:
            return jsonify({
                'error':
                f'Invalid datetime format: {appointment_datetime_str}. Use ISO format: YYYY-MM-DDTHH:MM:SS'
            }), 400

        # Insert appointment
        result = execute_insert(
            """INSERT INTO Appointment (AppointmentDateTime, Status, DoctorID, PatientID)
               VALUES (%s, 'Scheduled', %s, %s) 
               RETURNING AppointmentID, AppointmentDateTime, Status""",
            (appointment_datetime, doctor_id, patient_id))

        if not result:
            return jsonify({'error': 'Failed to create appointment'}), 500

        # Create bill for consultation fee
        doctor_info = safe_execute_query(
            "SELECT ConsultationFee FROM Doctor WHERE EmpID = %s",
            (doctor_id, ))

        if doctor_info:
            fee = doctor_info[0]['consultationfee']
            execute_insert(
                """INSERT INTO Bill (AppointmentID, Amount, BillDate, PaymentStatus)
                   VALUES (%s, %s, CURRENT_DATE, 'Unpaid')""",
                (result['appointmentid'], fee))

        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': dict(result)
        }), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        error_msg = str(e)
        # Handle trigger validation errors
        if 'already has 5 scheduled appointments' in error_msg:
            return jsonify(
                {'error':
                 'Doctor has reached daily appointment limit (5)'}), 400
        elif 'already has an active appointment' in error_msg:
            return jsonify(
                {'error': 'You already have an appointment on this date'}), 400
        elif 'not available at this appointment datetime' in error_msg:
            return jsonify({'error':
                            'Doctor is not available at this time'}), 400
        elif 'conflicts with another appointment' in error_msg:
            return jsonify(
                {'error':
                 'Time slot unavailable (30-minute buffer required)'}), 400
        return jsonify({'error': error_msg}), 500


@patient_bp.route('/appointments', methods=['GET'])
@token_required
@role_required('Patient')
def get_appointments():
    """Get patient's appointments"""
    try:
        user_id = get_user_id()

        # Get patient ID
        patient = safe_execute_query(
            "SELECT PatientID FROM Patient WHERE UserID = %s", (user_id, ))

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        patient_id: int = int(patient[0]['patientid'])

        # Get appointments
        appointments = safe_execute_query(
            """SELECT a.AppointmentID, a.AppointmentDateTime, a.Status,
                      a.PrescriptionText, a.RescheduleCount, a.CreatedAt,
                      e.Name as DoctorName, d.Specialization, d.ConsultationFee,
                      r.RoomName, dep.DeptName
               FROM Appointment a
               JOIN Doctor d ON a.DoctorID = d.EmpID
               JOIN Employee e ON d.EmpID = e.EmpID
               LEFT JOIN Room r ON d.RoomID = r.RoomID
               LEFT JOIN Department dep ON e.DeptID = dep.DeptID
               WHERE a.PatientID = %s
               ORDER BY a.AppointmentDateTime DESC""", (patient_id, ))

        return jsonify([dict(a) for a in appointments]), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@token_required
@role_required('Patient')
def cancel_appointment(appointment_id: int):
    """Cancel an appointment"""
    try:
        user_id = get_user_id()

        # Get patient ID
        patient = safe_execute_query(
            "SELECT PatientID FROM Patient WHERE UserID = %s", (user_id, ))

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        patient_id: int = int(patient[0]['patientid'])

        # Verify appointment ownership
        appointment = safe_execute_query(
            "SELECT Status FROM Appointment WHERE AppointmentID = %s AND PatientID = %s",
            (appointment_id, patient_id))

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        if appointment[0]['status'] == 'Cancelled':
            return jsonify({'error': 'Appointment already cancelled'}), 400

        # Cancel appointment
        execute_query(
            "UPDATE Appointment SET Status = 'Cancelled', UpdatedAt = %s WHERE AppointmentID = %s",
            (datetime.now(), appointment_id),
            fetch=False)

        return jsonify({'message': 'Appointment cancelled successfully'}), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/appointments/<int:appointment_id>/reschedule',
                  methods=['PUT'])
@token_required
@role_required('Patient')
def reschedule_appointment(appointment_id: int):
    """Reschedule an appointment"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        user_id = get_user_id()
        new_datetime_str = data.get('new_datetime')

        if not new_datetime_str:
            return jsonify({'error': 'new_datetime is required'}), 400

        # Parse new datetime
        try:
            clean_dt_str = new_datetime_str.split('+')[0].split('Z')[0]
            new_datetime = datetime.fromisoformat(clean_dt_str)
        except ValueError:
            return jsonify({
                'error':
                f'Invalid datetime format: {new_datetime_str}. Use ISO format: YYYY-MM-DDTHH:MM:SS'
            }), 400

        # Get patient ID
        patient = safe_execute_query(
            "SELECT PatientID FROM Patient WHERE UserID = %s", (user_id, ))

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        patient_id: int = int(patient[0]['patientid'])

        # Verify appointment ownership
        appointment = safe_execute_query(
            "SELECT Status FROM Appointment WHERE AppointmentID = %s AND PatientID = %s",
            (appointment_id, patient_id))

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        if appointment[0]['status'] == 'Cancelled':
            return jsonify(
                {'error': 'Cannot reschedule cancelled appointment'}), 400

        # Reschedule appointment (trigger will increment RescheduleCount and set Status)
        execute_query(
            "UPDATE Appointment SET AppointmentDateTime = %s WHERE AppointmentID = %s",
            (new_datetime, appointment_id),
            fetch=False)

        # Get updated appointment info
        updated = safe_execute_query(
            "SELECT Status, RescheduleCount FROM Appointment WHERE AppointmentID = %s",
            (appointment_id, ))

        return jsonify({
            'message':
            'Appointment rescheduled successfully',
            'status':
            updated[0]['status'] if updated else 'Rescheduled',
            'reschedule_count':
            updated[0]['reschedulecount'] if updated else None
        }), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        error_msg = str(e)
        # Handle trigger validation errors
        if 'already has 5 scheduled appointments' in error_msg:
            return jsonify(
                {'error':
                 'Doctor has reached daily appointment limit (5)'}), 400
        elif 'already has an active appointment' in error_msg:
            return jsonify(
                {'error': 'You already have an appointment on this date'}), 400
        elif 'not available at this appointment datetime' in error_msg:
            return jsonify({'error':
                            'Doctor is not available at this time'}), 400
        elif 'conflicts with another appointment' in error_msg:
            return jsonify(
                {'error':
                 'Time slot unavailable (30-minute buffer required)'}), 400
        return jsonify({'error': error_msg}), 500


@patient_bp.route('/bills', methods=['GET'])
@token_required
@role_required('Patient')
def get_bills():
    """Get patient's bills"""
    try:
        user_id = get_user_id()

        # Get patient ID
        patient = safe_execute_query(
            "SELECT PatientID FROM Patient WHERE UserID = %s", (user_id, ))

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        patient_id: int = int(patient[0]['patientid'])

        # Get bills
        bills = safe_execute_query(
            """SELECT b.BillID, b.Amount, b.BillDate, b.PaymentStatus, b.PaymentMethod,
                      b.AppointmentID, b.AdmissionID,
                      a.AppointmentDateTime, 
                      e.Name as DoctorName, d.Specialization
               FROM Bill b
               LEFT JOIN Appointment a ON b.AppointmentID = a.AppointmentID
               LEFT JOIN Doctor d ON a.DoctorID = d.EmpID
               LEFT JOIN Employee e ON d.EmpID = e.EmpID
               WHERE (a.PatientID = %s OR b.AdmissionID IN 
                     (SELECT AdmissionID FROM Admission WHERE PatientID = %s))
               ORDER BY b.BillDate DESC""", (patient_id, patient_id))

        return jsonify([dict(b) for b in bills]), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@patient_bp.route('/bills/<int:bill_id>/pay', methods=['PUT'])
@token_required
@role_required('Patient')
def pay_bill(bill_id: int):
    """Pay a bill"""
    try:
        data = request.get_json() or {}
        payment_method = data.get('payment_method', 'Cash')
        user_id = get_user_id()

        # Validate payment method
        valid_methods = [
            'Cash', 'Credit Card', 'Debit Card', 'Insurance', 'Online', 'Other'
        ]
        if payment_method not in valid_methods:
            return jsonify({
                'error':
                f'Invalid payment method. Must be one of: {", ".join(valid_methods)}'
            }), 400

        # Get patient ID
        patient = safe_execute_query(
            "SELECT PatientID FROM Patient WHERE UserID = %s", (user_id, ))

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        patient_id: int = int(patient[0]['patientid'])

        # Verify bill ownership
        bill_check = safe_execute_query(
            """SELECT b.BillID, b.PaymentStatus,
                      a.PatientID as AppointmentPatient, 
                      adm.PatientID as AdmissionPatient
               FROM Bill b
               LEFT JOIN Appointment a ON b.AppointmentID = a.AppointmentID
               LEFT JOIN Admission adm ON b.AdmissionID = adm.AdmissionID
               WHERE b.BillID = %s""", (bill_id, ))

        if not bill_check:
            return jsonify({'error': 'Bill not found'}), 404

        bill_data = bill_check[0]
        appt_patient = bill_data.get('appointmentpatient')
        adm_patient = bill_data.get('admissionpatient')

        # Check ownership
        owns_bill = (appt_patient == patient_id) or (adm_patient == patient_id)

        if not owns_bill:
            return jsonify(
                {'error':
                 'Access denied: This bill does not belong to you'}), 403

        # Check if already paid
        if bill_data['paymentstatus'] == 'Paid':
            return jsonify({'error': 'Bill is already paid'}), 400

        # Update bill
        execute_query(
            "UPDATE Bill SET PaymentStatus = 'Paid', PaymentMethod = %s WHERE BillID = %s",
            (payment_method, bill_id),
            fetch=False)

        return jsonify({
            'message': 'Bill paid successfully',
            'bill_id': bill_id,
            'payment_method': payment_method
        }), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
