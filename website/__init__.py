from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "master.db"


def create_app():
    # Create an instance of the Flask application
    app = Flask(__name__)

    # Set the secret key to secure sessions and forms
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    
    # Set the database URI to use SQLite with a dynamic database name
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Initialize the database with the Flask app
    db.init_app(app)

    # Import the views and authentication blueprint modules
    from .auth import auth
    from .pick_home import pick_home
    
    app.register_blueprint(pick_home, url_prfix = '/')
    
    # Register the 'auth' blueprint with the root URL ('/')
    app.register_blueprint(auth, url_prefix='/')

    # Import the User and Note models (used for database tables)
    from .models import User, Note

    # Create all database tables if they do not already exist, within the app's context
    with app.app_context():
        db.create_all()

    # Initialize the login manager to handle user sessions
    login_manager = LoginManager()
    
    # Set the view that users are redirected to if not logged in (login page)
    login_manager.login_view = 'auth.login'
    
    # Initialize the login manager with the Flask app
    login_manager.init_app(app)

    # Define a user loader function that retrieves a user from the database by ID
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Return the fully configured Flask app
    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
