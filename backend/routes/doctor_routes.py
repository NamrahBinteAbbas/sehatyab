from flask import Blueprint, request, jsonify
from database import execute_query, execute_insert
from utils.auth import token_required, role_required
from datetime import datetime, timedelta
from typing import Any, List, Optional, cast
from psycopg2.extras import RealDictRow

doctor_bp = Blueprint('doctor', __name__)


def get_user_id() -> int:
    """Helper to safely extract user_id from request"""
    user_data = getattr(request, 'user', None)
    if not user_data or not isinstance(user_data, dict):
        raise ValueError("User authentication data not found")
    user_id = user_data.get('user_id')
    if not isinstance(user_id, int):
        raise ValueError("Invalid user ID")
    return user_id


def get_username() -> str:
    """Helper to safely extract username from request"""
    user_data = getattr(request, 'user', None)
    if not user_data or not isinstance(user_data, dict):
        return 'unknown'
    return str(user_data.get('username', 'unknown'))


def safe_execute_query(query: str, params: tuple) -> List[RealDictRow]:
    """Execute query and ensure it returns a list"""
    result = execute_query(query, params)
    if isinstance(result, list):
        return result
    return []


@doctor_bp.route('/profile', methods=['GET'])
@token_required
@role_required('Doctor')
def get_profile():
    """Get doctor profile information"""
    try:
        user_id = get_user_id()

        profile = safe_execute_query(
            """SELECT e.EmpID, e.Name, e.Gender, e.Role, e.Contact, e.Salary, 
                      e.DeptID, e.IsActive, e.CreatedAt,
                      d.Specialization, d.Qualification, d.RoomID, d.ConsultationFee,
                      r.RoomName, dep.DeptName
               FROM Employee e
               JOIN Doctor d ON e.EmpID = d.EmpID
               LEFT JOIN Room r ON d.RoomID = r.RoomID
               LEFT JOIN Department dep ON e.DeptID = dep.DeptID
               WHERE e.UserID = %s AND e.IsActive = 'Y'""", (user_id, ))

        if not profile:
            return jsonify({'error': 'Doctor profile not found'}), 404

        return jsonify(dict(profile[0])), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/appointments', methods=['GET'])
@token_required
@role_required('Doctor')
def get_appointments():
    """Get doctor's appointments (filtered by date if provided)"""
    try:
        user_id = get_user_id()
        date: Optional[str] = request.args.get('date')

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Build query
        query = """
            SELECT a.AppointmentID, a.AppointmentDateTime, a.Status, 
                   a.PrescriptionText, a.RescheduleCount, a.CreatedAt,
                   p.PatientID, p.Name as PatientName, p.Age, p.Gender, 
                   p.ContactNo, p.BloodGroup, p.Address, p.EmergencyContact
            FROM Appointment a
            JOIN Patient p ON a.PatientID = p.PatientID
            WHERE a.DoctorID = %s
        """
        params: List[Any] = [doctor_id]

        if date:
            query += " AND DATE(a.AppointmentDateTime) = %s"
            params.append(date)
        else:
            query += " AND DATE(a.AppointmentDateTime) >= CURRENT_DATE"

        query += " ORDER BY a.AppointmentDateTime"

        appointments = safe_execute_query(query, tuple(params))

        return jsonify([dict(a) for a in appointments]), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/appointments/weekly', methods=['GET'])
@token_required
@role_required('Doctor')
def get_weekly_schedule():
    """Get doctor's weekly appointment schedule"""
    try:
        user_id = get_user_id()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Calculate week range (Monday to Sunday)
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        appointments = safe_execute_query(
            """SELECT a.AppointmentID, a.AppointmentDateTime, a.Status, 
                      a.PrescriptionText, a.RescheduleCount,
                      p.PatientID, p.Name as PatientName, p.Age, 
                      p.Gender, p.ContactNo, p.BloodGroup
               FROM Appointment a
               JOIN Patient p ON a.PatientID = p.PatientID
               WHERE a.DoctorID = %s
                 AND DATE(a.AppointmentDateTime) BETWEEN %s AND %s
               ORDER BY a.AppointmentDateTime""",
            (doctor_id, week_start, week_end))

        return jsonify([dict(a) for a in appointments]), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/appointments/<int:appointment_id>/prescription',
                 methods=['PUT'])
@token_required
@role_required('Doctor')
def write_prescription(appointment_id: int):
    """Add prescription to an appointment and mark as completed"""
    try:
        data = request.get_json(silent=True) or {}
        prescription_text: Optional[str] = data.get('prescription_text')

        if not prescription_text or not prescription_text.strip():
            return jsonify({'error': 'Prescription text is required'}), 400

        user_id = get_user_id()
        username = get_username()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Get appointment details with datetime and status
        appointments = safe_execute_query(
            """SELECT AppointmentDateTime, Status, PrescriptionText
               FROM Appointment 
               WHERE AppointmentID = %s AND DoctorID = %s""",
            (appointment_id, doctor_id))

        if not appointments:
            return jsonify({'error':
                            'Appointment not found or unauthorized'}), 404

        appt = appointments[0]
        appt_dt_raw = appt['appointmentdatetime']  # string after serialization
        status = str(appt['status'])
        existing_prescription = appt.get('prescriptiontext')

        # Parse ISO datetime string from DB into datetime object
        try:
            # Expecting "YYYY-MM-DDTHH:MM:SS"
            appt_dt = datetime.fromisoformat(appt_dt_raw)
        except Exception:
            return jsonify({'error':
                            'Invalid appointment datetime format'}), 500

        # Validate appointment status
        if status == 'Cancelled':
            return jsonify({
                'error':
                'Cannot write prescription for a cancelled appointment'
            }), 400

        # Handle timezone-aware comparison
        if appt_dt.tzinfo is not None:
            now_dt = datetime.now(appt_dt.tzinfo)
        else:
            now_dt = datetime.now()

        # Validation: Can only write prescription at or after appointment time
        if now_dt < appt_dt:
            time_until = appt_dt - now_dt
            hours_until = int(time_until.total_seconds() / 3600)
            return jsonify({
                'error':
                ('You can only write prescription at or after the appointment time. '
                 f'Appointment is in {hours_until} hours.')
            }), 400

        # Optional: Prevent writing prescriptions too long after appointment
        max_window_days = 7
        time_since = now_dt - appt_dt
        if time_since.days > max_window_days:
            return jsonify({
                'error':
                (f'Cannot write prescription more than {max_window_days} days after appointment. '
                 f'This appointment was {time_since.days} days ago.')
            }), 400

        # Optional: Warn if overwriting existing prescription
        if existing_prescription and str(existing_prescription).strip():
            force_overwrite = bool(data.get('force_overwrite', False))
            if not force_overwrite:
                return jsonify({
                    'error':
                    'Prescription already exists for this appointment',
                    'existing_prescription':
                    str(existing_prescription),
                    'hint':
                    'Set force_overwrite=true to update'
                }), 409

        # Update appointment with prescription
        execute_query("""UPDATE Appointment 
               SET PrescriptionText = %s, 
                   Status = 'Completed', 
                   UpdatedAt = %s
               WHERE AppointmentID = %s""",
                      (prescription_text.strip(), now_dt, appointment_id),
                      fetch=False)

        # Optional: Log to audit table
        try:
            execute_query("""INSERT INTO Appointment_Audit 
                       (AppointmentID, ActionType, OldStatus, NewStatus, ChangedBy, ChangeDate)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                          (appointment_id, 'PRESCRIPTION_ADDED', status,
                           'Completed', username, now_dt),
                          fetch=False)
        except Exception as audit_err:
            # Don't fail the main operation if audit logging fails
            print(f"Audit logging failed: {audit_err}")

        return jsonify({
            'message': 'Prescription added successfully',
            'appointment_id': appointment_id,
            'status': 'Completed',
            'prescription_text': prescription_text.strip(),
            'updated_at': now_dt.isoformat()
        }), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        error_msg = str(e)
        if 'foreign key' in error_msg.lower():
            return jsonify(
                {'error': 'Invalid appointment or doctor reference'}), 400
        return jsonify({'error': error_msg}), 500


@doctor_bp.route('/availability', methods=['GET'])
@token_required
@role_required('Doctor')
def get_availability():
    """Get doctor's availability schedule"""
    try:
        user_id = get_user_id()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Get future availability
        availability = safe_execute_query(
            """SELECT AvailabilityID, DoctorID, AvailableDate, 
                      StartTime, EndTime
               FROM DoctorAvailability
               WHERE DoctorID = %s AND AvailableDate >= CURRENT_DATE
               ORDER BY AvailableDate, StartTime""", (doctor_id, ))

        return jsonify([dict(a) for a in availability]), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/availability', methods=['POST'])
@token_required
@role_required('Doctor')
def add_availability():
    """Add new availability slot for doctor"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        user_id = get_user_id()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Extract and validate input
        available_date = data.get('available_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([available_date, start_time, end_time]):
            return jsonify({
                'error':
                'Missing required fields: available_date, start_time, end_time'
            }), 400

        # Type check after validation
        if not isinstance(available_date, str) or not isinstance(
                start_time, str) or not isinstance(end_time, str):
            return jsonify({'error': 'All fields must be strings'}), 400

        # Validate date format
        try:
            date_obj = datetime.strptime(available_date, '%Y-%m-%d').date()
            if date_obj < datetime.now().date():
                return jsonify(
                    {'error': 'Cannot add availability for past dates'}), 400
        except ValueError:
            return jsonify({'error':
                            'Invalid date format. Use YYYY-MM-DD'}), 400

        # Validate time format
        try:
            datetime.strptime(start_time, '%H:%M:%S')
            datetime.strptime(end_time, '%H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM:SS'}), 400

        # Insert availability (triggers will validate time range and uniqueness)
        result = execute_insert(
            """INSERT INTO DoctorAvailability 
                   (DoctorID, AvailableDate, StartTime, EndTime)
               VALUES (%s, %s, %s, %s) 
               RETURNING AvailabilityID""",
            (doctor_id, available_date, start_time, end_time))

        if not result or not isinstance(result, dict):
            return jsonify({'error': 'Failed to create availability'}), 500

        return jsonify({
            'message': 'Availability added successfully',
            'availability_id': result.get('availabilityid'),
            'available_date': available_date,
            'start_time': start_time,
            'end_time': end_time
        }), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        # Handle database constraint violations
        error_msg = str(e)
        if 'duplicate key value' in error_msg.lower():
            return jsonify(
                {'error': 'Availability already exists for this date'}), 409
        elif 'chk_avail_time' in error_msg.lower():
            return jsonify({'error':
                            'Start time must be before end time'}), 400

        return jsonify({'error': error_msg}), 500


@doctor_bp.route('/availability/<int:availability_id>', methods=['PUT'])
@token_required
@role_required('Doctor')
def update_availability(availability_id: int):
    """Update existing availability slot"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        user_id = get_user_id()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Verify ownership
        existing = safe_execute_query(
            """SELECT * FROM DoctorAvailability 
               WHERE AvailabilityID = %s AND DoctorID = %s""",
            (availability_id, doctor_id))

        if not existing:
            return jsonify({'error': 'Availability slot not found'}), 404

        # Build update query dynamically
        update_fields: List[str] = []
        params: List[Any] = []

        if 'available_date' in data:
            update_fields.append("AvailableDate = %s")
            params.append(data['available_date'])

        if 'start_time' in data:
            update_fields.append("StartTime = %s")
            params.append(data['start_time'])

        if 'end_time' in data:
            update_fields.append("EndTime = %s")
            params.append(data['end_time'])

        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400

        params.append(availability_id)

        execute_query(f"""UPDATE DoctorAvailability 
                SET {', '.join(update_fields)}
                WHERE AvailabilityID = %s""",
                      tuple(params),
                      fetch=False)

        return jsonify({
            'message': 'Availability updated successfully',
            'availability_id': availability_id
        }), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/availability/<int:availability_id>', methods=['DELETE'])
@token_required
@role_required('Doctor')
def delete_availability(availability_id: int):
    """Delete availability slot (only if no appointments scheduled)"""
    try:
        user_id = get_user_id()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Verify ownership
        existing = safe_execute_query(
            """SELECT AvailableDate FROM DoctorAvailability 
               WHERE AvailabilityID = %s AND DoctorID = %s""",
            (availability_id, doctor_id))

        if not existing:
            return jsonify({'error': 'Availability slot not found'}), 404

        avail_date = existing[0]['availabledate']

        # Check for scheduled appointments
        appointments = safe_execute_query(
            """SELECT COUNT(*) as count FROM Appointment 
               WHERE DoctorID = %s 
                 AND DATE(AppointmentDateTime) = %s
                 AND Status IN ('Scheduled', 'Rescheduled')""",
            (doctor_id, avail_date))

        if appointments and int(appointments[0]['count']) > 0:
            return jsonify({
                'error':
                'Cannot delete availability with scheduled appointments'
            }), 409

        # Delete availability
        execute_query(
            "DELETE FROM DoctorAvailability WHERE AvailabilityID = %s",
            (availability_id, ),
            fetch=False)

        return jsonify({'message': 'Availability deleted successfully'}), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@doctor_bp.route('/stats', methods=['GET'])
@token_required
@role_required('Doctor')
def get_stats():
    """Get doctor's statistics"""
    try:
        user_id = get_user_id()

        # Get doctor's EmpID
        doctor = safe_execute_query(
            "SELECT EmpID FROM Employee WHERE UserID = %s AND IsActive = 'Y'",
            (user_id, ))

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        doctor_id: int = int(doctor[0]['empid'])

        # Get various statistics
        stats = safe_execute_query(
            """SELECT 
                   COUNT(*) FILTER (WHERE Status = 'Scheduled') as scheduled_count,
                   COUNT(*) FILTER (WHERE Status = 'Completed') as completed_count,
                   COUNT(*) FILTER (WHERE Status = 'Cancelled') as cancelled_count,
                   COUNT(*) FILTER (WHERE DATE(AppointmentDateTime) = CURRENT_DATE) as today_count,
                   COUNT(*) FILTER (WHERE DATE(AppointmentDateTime) = CURRENT_DATE + 1) as tomorrow_count
               FROM Appointment
               WHERE DoctorID = %s""", (doctor_id, ))

        if not stats:
            return jsonify({
                'scheduled_count': 0,
                'completed_count': 0,
                'cancelled_count': 0,
                'today_count': 0,
                'tomorrow_count': 0
            }), 200

        return jsonify(dict(stats[0])), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
