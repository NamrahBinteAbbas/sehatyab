from flask import Blueprint, request, jsonify
from database import execute_query, execute_insert
from utils.auth import hash_password, verify_password, generate_token
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        user_type = data.get('user_type')
        
        if user_type not in ['Patient', 'Doctor', 'Admin']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password, user_type]):
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
            (username, email, hashed_pwd, user_type)
        )
        
        user_id = user_result['userid']
        
        if user_type == 'Patient':
            name = data.get('name')
            age = data.get('age')
            gender = data.get('gender')
            address = data.get('address', '')
            contact_no = data.get('contact_no')
            blood_group = data.get('blood_group')
            emergency_contact = data.get('emergency_contact', '')
            
            if not all([name, age, gender, contact_no]):
                execute_query("UPDATE UserAuth SET IsActive = 'N' WHERE UserID = %s", (user_id,), fetch=False)
                return jsonify({'error': 'Missing patient information'}), 400
            
            execute_insert(
                """INSERT INTO Patient (UserID, Name, Age, Gender, Address, ContactNo, BloodGroup, EmergencyContact, IsActive)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Y')""",
                (user_id, name, age, gender, address, contact_no, blood_group, emergency_contact)
            )
        
        elif user_type == 'Admin':
            return jsonify({'error': 'Admin accounts must be created by existing admin'}), 403
        
        elif user_type == 'Doctor':
            return jsonify({'error': 'Doctor accounts must be created by admin'}), 403
        
        token = generate_token(user_id, user_type, email)
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'user_id': user_id,
                'username': username,
                'email': email,
                'user_type': user_type
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = execute_query(
            "SELECT UserID, Username, Email, PasswordHash, UserType, IsActive FROM UserAuth WHERE Username = %s",
            (username,)
        )
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = user[0]
        
        if user['isactive'] != 'Y':
            return jsonify({'error': 'Account is inactive'}), 403
        
        if not verify_password(password, user['passwordhash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        execute_query(
            "UPDATE UserAuth SET LastLogin = %s WHERE UserID = %s",
            (datetime.now(), user['userid']),
            fetch=False
        )
        
        token = generate_token(user['userid'], user['usertype'], user['email'])
        
        user_details = None
        if user['usertype'] == 'Patient':
            patient = execute_query("SELECT * FROM Patient WHERE UserID = %s", (user['userid'],))
            if patient:
                user_details = dict(patient[0])
        elif user['usertype'] == 'Doctor':
            doctor = execute_query(
                """SELECT e.*, d.Specialization, d.Qualification, d.RoomID, d.ConsultationFee
                   FROM Employee e
                   JOIN Doctor d ON e.EmpID = d.EmpID
                   WHERE e.UserID = %s""",
                (user['userid'],)
            )
            if doctor:
                user_details = dict(doctor[0])
        elif user['usertype'] == 'Admin':
            admin = execute_query(
                """SELECT e.*, a.CanManageDoctors, a.CanManageRooms, a.CanViewReports
                   FROM Employee e
                   JOIN Admin a ON e.EmpID = a.EmpID
                   WHERE e.UserID = %s""",
                (user['userid'],)
            )
            if admin:
                user_details = dict(admin[0])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user['userid'],
                'username': user['username'],
                'email': user['email'],
                'user_type': user['usertype'],
                'details': user_details
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
