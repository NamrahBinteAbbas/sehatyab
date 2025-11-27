from flask import Flask, render_template
from flask_cors import CORS
from websites.views import views
from websites.auth import auth
from db import test_connection
from doctor_api import doctor_bp


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'namrahsapp'

# Register blueprints (ensure these are Blueprint instances in your modules)
app.register_blueprint(auth)   # maybe add url_prefix="/" inside the blueprint
app.register_blueprint(views)  # maybe add url_prefix="/dashboard" inside the blueprint

# Correct decorator + friendlier URL path
@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route("/test-db")
def test_db():
    try:
        now = test_connection()
        return f"Connected! Server time is: {now}"
    except Exception as e:
        return f"DB ERROR: {e}", 500

if __name__ == "__main__":
    print("[INFO] Starting Flask app...")
    app.run(debug=True)
