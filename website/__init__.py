# Initialize the app from here
from flask import Flask

# Create flask app
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'namrahsapp'
    
    from .views import views
    app.register_blueprint(views, url_prefix='/')
    
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')
    
    return app