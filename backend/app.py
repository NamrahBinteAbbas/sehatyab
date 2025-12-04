from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.admin_routes import admin_bp
from routes.doctor_routes import doctor_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(patient_bp, url_prefix='/api/patient')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')

@app.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'message': 'Sehatyaab Hospital Management System'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
