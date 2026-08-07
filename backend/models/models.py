from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'company', 'student'
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")

class CompanyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    hr_name = db.Column(db.String(100))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    logo_path = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=False)
    
    drives = db.relationship('PlacementDrive', backref='company', cascade="all, delete-orphan")

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)
    resume_link = db.Column(db.String(255))
    resume_file_path = db.Column(db.String(255))
    profile_photo_path = db.Column(db.String(255))
    
    applications = db.relationship('Application', backref='student', cascade="all, delete-orphan")

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    package_lpa = db.Column(db.Float)
    location = db.Column(db.String(100))
    branch_eligibility = db.Column(db.String(200)) # comma-separated
    cgpa_cutoff = db.Column(db.Float, default=0.0)
    application_deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='drive', cascade="all, delete-orphan")

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied') # 'Applied', 'Shortlisted', 'Selected', 'Rejected'
    
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='_student_drive_uc'),)
