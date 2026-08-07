import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from config import Config
from models.models import db, User
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp
from extensions import cache

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
    
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='/')
    app.config.from_object(Config)
    
    # folder for uploaded resumes and logos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    cache.init_app(app)
    
    # register routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
        
    @app.route('/src/<path:filename>')
    def serve_static(filename):
        return app.send_static_file(f'src/{filename}')
        
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
        
    # make database and default admin user if not exists
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email='admin@ppa.edu').first()
        if not admin:
            admin = User(
                email='admin@ppa.edu',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
