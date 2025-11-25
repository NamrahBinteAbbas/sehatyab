# Main entry point of the application
from website import create_app, get_db_connection

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)