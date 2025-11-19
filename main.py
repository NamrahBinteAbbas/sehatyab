from flask import Flask, Blueprint, render_template
from flask_cors import CORS
from websites.views import views
from websites.auth import auth

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'namrahsapp'

# register blueprints
app.register_blueprint(auth)   # for '/' route
app.register_blueprint(views)  # for '/dashboard' route

app.route('/admin.html')
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    print("[INFO] Starting Flask app...")
    app.run(debug=True)
