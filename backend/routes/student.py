from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, StudentProfile, PlacementDrive, Application
from functools import wraps
from datetime import datetime
import os
import csv
import io
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

# helper to check if user is a student
def student_only(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return jsonify({"msg": "Student access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@student_bp.route('/profile', methods=['GET'])
@student_only
def get_profile():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    profile = user.student_profile
    return jsonify({
        "name": profile.name,
        "branch": profile.branch,
        "cgpa": profile.cgpa,
        "year": profile.year,
        "resume_link": profile.resume_link,
        "resume_file_path": profile.resume_file_path,
        "profile_photo_path": profile.profile_photo_path
    }), 200

@student_bp.route('/profile', methods=['PUT'])
@student_only
def update_profile():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    profile = user.student_profile
    
    # check if they are uploading files
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
        BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
        # save photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(f"student_photo_{user.id}_{file.filename}")
                file_path = os.path.join(BASE_DIR, 'uploads', filename)
                file.save(file_path)
                profile.profile_photo_path = f"/uploads/{filename}"
                
        # save resume
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                filename = secure_filename(f"student_resume_{user.id}_{file.filename}")
                file_path = os.path.join(BASE_DIR, 'uploads', filename)
                file.save(file_path)
                profile.resume_file_path = f"/uploads/{filename}"
    else:
        data = request.json
    
    # update fields if they exist
    if data:
        if 'name' in data: profile.name = data['name']
        if 'branch' in data: profile.branch = data['branch']
        if 'cgpa' in data: profile.cgpa = data['cgpa']
        if 'year' in data: profile.year = data['year']
        if 'resume_link' in data: profile.resume_link = data['resume_link']
    
    db.session.commit()
    return jsonify({"msg": "Updated"}), 200

@student_bp.route('/drives', methods=['GET'])
@student_only
def get_drives():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    profile = user.student_profile
    
    # get drives that are not expired and approved
    today = datetime.now().date()
    drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= today
    ).all()
    
    res = []
    for d in drives:
        eligible = True
        if d.cgpa_cutoff > (profile.cgpa or 0):
            eligible = False
        if d.branch_eligibility:
            branches = [b.strip() for b in d.branch_eligibility.split(',')]
            if profile.branch not in branches:
                eligible = False
                
        applied = any(a.student_id == profile.id for a in d.applications)
        
        res.append({
            "id": d.id,
            "company_name": d.company.name,
            "company_logo": d.company.logo_path,
            "job_title": d.job_title,
            "description": d.description,
            "package_lpa": d.package_lpa,
            "location": d.location,
            "cgpa_cutoff": d.cgpa_cutoff,
            "branch_eligibility": d.branch_eligibility,
            "application_deadline": d.application_deadline.strftime('%Y-%m-%d'),
            "eligible": eligible,
            "applied": applied
        })
    return jsonify(res), 200

@student_bp.route('/drives/<int:id>/apply', methods=['POST'])
@student_only
def apply_drive(id):
    identity = get_jwt_identity()
    user = User.query.get(identity)
    profile = user.student_profile
    
    drive = PlacementDrive.query.get_or_404(id)
    
    if drive.status != 'Approved':
        return jsonify({"msg": "Drive not approved"}), 400
        
    if drive.application_deadline < datetime.now().date():
        return jsonify({"msg": "Deadline passed"}), 400
        
    if drive.cgpa_cutoff > (profile.cgpa or 0):
        return jsonify({"msg": "Not eligible by CGPA"}), 400
        
    if drive.branch_eligibility:
        branches = [b.strip() for b in drive.branch_eligibility.split(',')]
        if profile.branch not in branches:
            return jsonify({"msg": "Not eligible by branch"}), 400
            
    # check if they already applied
    existing = Application.query.filter_by(student_id=profile.id, drive_id=id).first()
    if existing:
        return jsonify({"msg": "Already applied"}), 400
        
    app = Application(student_id=profile.id, drive_id=id)
    db.session.add(app)
    db.session.commit()
    return jsonify({"msg": "Applied successfully"}), 201

@student_bp.route('/applications', methods=['GET'])
@student_only
def get_applications():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    apps = Application.query.filter_by(student_id=user.student_profile.id).all()
    
    res = []
    for app in apps:
        res.append({
            "id": app.id,
            "company_name": app.drive.company.name,
            "job_title": app.drive.job_title,
            "package_lpa": app.drive.package_lpa,
            "status": app.status,
            "application_date": app.application_date.strftime('%Y-%m-%d')
        })
    return jsonify(res), 200

@student_bp.route('/export-csv', methods=['POST'])
@student_only
def export_csv():
    # queue async celery job
    identity = get_jwt_identity()
    user = User.query.get(identity)
    profile = user.student_profile

    from tasks.celery_tasks import export_student_history_csv
    task = export_student_history_csv.delay(profile.id)
    return jsonify({"task_id": task.id}), 202

@student_bp.route('/export-csv/status/<task_id>', methods=['GET'])
@student_only
def export_csv_status(task_id):
    from tasks.celery_tasks import celery_app
    task = celery_app.AsyncResult(task_id)

    if task.state == 'PENDING':
        return jsonify({"state": "PENDING", "status": "Waiting for worker..."}), 200
    elif task.state == 'SUCCESS':
        return jsonify({"state": "SUCCESS", "result": task.result}), 200
    elif task.state == 'FAILURE':
        return jsonify({"state": "FAILURE", "status": str(task.info)}), 500
    else:
        return jsonify({"state": task.state, "status": "In progress..."}), 200
