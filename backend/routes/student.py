from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, StudentProfile, PlacementDrive, Application
from functools import wraps
from datetime import datetime
import os
import csv
import io
from werkzeug.utils import secure_filename
from extensions import cache

student_bp = Blueprint('student', __name__)

# helper to check if user is a student
def student_only(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'student':
            return jsonify({"msg": "Student access required"}), 403
            
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user:
            return jsonify({"msg": "User not found"}), 401
        if not user.active:
            return jsonify({"msg": "User account is disabled"}), 403
            
        return fn(*args, **kwargs)
    return wrapper

@student_bp.route('/profile', methods=['GET'])
@student_only
def fetch_my_profile():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.student_profile
    return jsonify({
        "name": profile_data.name,
        "branch": profile_data.branch,
        "cgpa": profile_data.cgpa,
        "year": profile_data.year,
        "resume_link": profile_data.resume_link,
        "resume_file_path": profile_data.resume_file_path,
        "profile_photo_path": profile_data.profile_photo_path
    }), 200

@student_bp.route('/profile', methods=['PUT'])
@student_only
def edit_my_profile():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.student_profile
    
    # check if they are uploading files
    if request.content_type and 'multipart/form-data' in request.content_type:
        print("MULTIPART REQUEST", flush=True)
        print("FORM:", request.form, flush=True)
        print("FILES:", request.files, flush=True)
        data = request.form
        BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
        # save photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(f"student_photo_{u_record.id}_{file.filename}")
                file_path = os.path.join(BASE_DIR, 'uploads', filename)
                file.save(file_path)
                profile_data.profile_photo_path = f"/uploads/{filename}"
                
        # save resume
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                filename = secure_filename(f"student_resume_{u_record.id}_{file.filename}")
                file_path = os.path.join(BASE_DIR, 'uploads', filename)
                file.save(file_path)
                profile_data.resume_file_path = f"/uploads/{filename}"
    else:
        data = request.json
    
    # update fields if they exist
    if data:
        if data.get('name') and data.get('name') not in ['null', 'undefined', '']: profile_data.name = data['name']
        if data.get('branch') and data.get('branch') not in ['null', 'undefined', '']: profile_data.branch = data['branch']
        if data.get('cgpa') and data.get('cgpa') not in ['null', 'undefined', '']: profile_data.cgpa = float(data['cgpa'])
        if data.get('year') and data.get('year') not in ['null', 'undefined', '']: profile_data.year = int(data['year'])
        if data.get('resume_link') and data.get('resume_link') not in ['null', 'undefined', '']: profile_data.resume_link = data['resume_link']
    
    db.session.commit()
    return jsonify({"msg": "Updated"}), 200

@student_bp.route('/drives', methods=['GET'])
@student_only
def load_all_drives():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.student_profile
    
    # get drives that are not expired and approved
    curr_date = datetime.now().date()
    placements = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.application_deadline >= curr_date
    ).all()
    
    output_list = []
    for pdrive in placements:
        eligible = True
        if pdrive.cgpa_cutoff > (profile_data.cgpa or 0):
            eligible = False
        if pdrive.branch_eligibility:
            branches = [b.strip() for b in pdrive.branch_eligibility.split(',')]
            if profile_data.branch not in branches:
                eligible = False

        # skip drives the student isn't eligible for
        if not eligible:
            continue
            
        # skip drives if the company is unapproved or banned
        if not pdrive.company.approved or not pdrive.company.user.active:
            continue

        applied = any(a.student_id == profile_data.id for a in pdrive.applications)

        output_list.append({
            "id": pdrive.id,
            "company_name": pdrive.company.name,
            "company_logo": pdrive.company.logo_path,
            "job_title": pdrive.job_title,
            "description": pdrive.description,
            "package_lpa": pdrive.package_lpa,
            "location": pdrive.location,
            "cgpa_cutoff": pdrive.cgpa_cutoff,
            "branch_eligibility": pdrive.branch_eligibility,
            "application_deadline": pdrive.application_deadline.strftime('%Y-%m-%d'),
            "applied": applied
        })
    return jsonify(output_list), 200

@student_bp.route('/drives/<int:id>/apply', methods=['POST'])
@student_only
def submit_application(id):
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.student_profile
    
    drive = PlacementDrive.query.get_or_404(id)
    
    if drive.status != 'Approved':
        return jsonify({"msg": "Drive not approved"}), 400
        
    if drive.application_deadline < datetime.now().date():
        return jsonify({"msg": "Deadline passed"}), 400
        
    if drive.cgpa_cutoff > (profile_data.cgpa or 0):
        return jsonify({"msg": "Not eligible by CGPA"}), 400
        
    if drive.branch_eligibility:
        branches = [b.strip() for b in drive.branch_eligibility.split(',')]
        if profile_data.branch not in branches:
            return jsonify({"msg": "Not eligible by branch"}), 400
            
    # check if they already applied
    existing = Application.query.filter_by(student_id=profile_data.id, drive_id=id).first()
    if existing:
        return jsonify({"msg": "Already applied"}), 400
        
    app = Application(student_id=profile_data.id, drive_id=id)
    db.session.add(app)
    db.session.commit()
    
    if cache:
        for k in ['admin_stats', 'admin_analytics', 'admin_drives']:
            cache.delete(k)
            
    return jsonify({"msg": "Applied successfully"}), 201

@student_bp.route('/applications', methods=['GET'])
@student_only
def fetch_my_applications():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    apps = Application.query.filter_by(student_id=u_record.student_profile.id).all()
    
    output_list = []
    for app in apps:
        warning = None
        if app.drive.status != 'Approved':
            warning = "Drive Unapproved"
        elif not app.drive.company.approved:
            warning = "Company Unapproved"
        elif not app.drive.company.user.active:
            warning = "Company Banned"
            
        output_list.append({
            "id": app.id,
            "company_name": app.drive.company.name,
            "job_title": app.drive.job_title,
            "package_lpa": app.drive.package_lpa,
            "status": app.status,
            "application_date": app.application_date.strftime('%Y-%m-%d'),
            "warning": warning
        })
    return jsonify(output_list), 200

@student_bp.route('/export-csv', methods=['POST'])
@student_only
def download_student_csv():
    # queue async celery job
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.student_profile

    from tasks.celery_tasks import export_student_history_csv as dl_csv_task
    task = dl_csv_task.delay(profile_data.id)
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
