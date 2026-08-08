from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, CompanyProfile, PlacementDrive, Application
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from extensions import cache

company_bp = Blueprint('company', __name__)

def company_only(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'company':
            return jsonify({"msg": "Company access required"}), 403
            
        # Verify user is still active and approved
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user:
            return jsonify({"msg": "User not found"}), 401
        if not user.active:
            return jsonify({"msg": "User account is disabled"}), 403
        if user.company_profile and not user.company_profile.approved:
            return jsonify({"msg": "Company account not approved yet"}), 403
            
        return fn(*args, **kwargs)
    return wrapper

@company_bp.route('/profile', methods=['GET'])
@company_only
def fetch_my_profile():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.company_profile
    return jsonify({
        "name": profile_data.name,
        "description": profile_data.description,
        "hr_name": profile_data.hr_name,
        "hr_contact": profile_data.hr_contact,
        "website": profile_data.website,
        "logo_path": profile_data.logo_path,
        "approved": profile_data.approved
    }), 200

@company_bp.route('/profile', methods=['PUT'])
@company_only
def edit_my_profile():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    profile_data = u_record.company_profile
    
    # check for logo upload
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                filename = secure_filename(f"company_{u_record.id}_{file.filename}")
                BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
                file_path = os.path.join(BASE_DIR, 'uploads', filename)
                file.save(file_path)
                profile_data.logo_path = f"/uploads/{filename}"
    else:
        data = request.json
    
    # update info
    if data:
        if data.get('name') and data.get('name') not in ['null', 'undefined', '']: profile_data.name = data['name']
        if data.get('description') and data.get('description') not in ['null', 'undefined', '']: profile_data.description = data['description']
        if data.get('hr_name') and data.get('hr_name') not in ['null', 'undefined', '']: profile_data.hr_name = data['hr_name']
        if data.get('hr_contact') and data.get('hr_contact') not in ['null', 'undefined', '']: profile_data.hr_contact = data['hr_contact']
        if data.get('website') and data.get('website') not in ['null', 'undefined', '']: profile_data.website = data['website']
    
    db.session.commit()
    return jsonify({"msg": "Updated"}), 200

@company_bp.route('/drives', methods=['GET'])
@company_only
def load_all_drives():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    placements = PlacementDrive.query.filter_by(company_id=u_record.company_profile.id).all()
    output_list = []
    for pdrive in placements:
        output_list.append({
            "id": pdrive.id,
            "job_title": pdrive.job_title,
            "description": pdrive.description,
            "package_lpa": pdrive.package_lpa,
            "location": pdrive.location,
            "branch_eligibility": pdrive.branch_eligibility,
            "cgpa_cutoff": pdrive.cgpa_cutoff,
            "application_deadline": pdrive.application_deadline.strftime('%Y-%m-%d') if pdrive.application_deadline else None,
            "status": pdrive.status,
            "applicant_count": len(pdrive.applications) if pdrive.status == 'Approved' else 0
        })
    return jsonify(output_list), 200

@company_bp.route('/drives', methods=['POST'])
@company_only
def add_new_drive():
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    data = request.json
    
    deadline_str = data.get('application_deadline')
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    
    if deadline < datetime.now().date():
        return jsonify({"msg": "Deadline must be in future"}), 400
        
    new_drive = PlacementDrive(
        company_id=u_record.company_profile.id,
        job_title=data.get('job_title'),
        description=data.get('description'),
        package_lpa=data.get('package_lpa'),
        location=data.get('location'),
        branch_eligibility=data.get('branch_eligibility'),
        cgpa_cutoff=data.get('cgpa_cutoff', 0.0),
        application_deadline=deadline
    )
    db.session.add(new_drive)
    db.session.commit()
    
    if cache:
        for k in ['admin_stats', 'admin_drives', 'admin_analytics']:
            cache.delete(k)
            
    return jsonify({"msg": "Drive created"}), 201

@company_bp.route('/drives/<int:id>/applications', methods=['GET'])
@company_only
def get_applications(id):
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    drive = PlacementDrive.query.get_or_404(id)
    
    if drive.company_id != u_record.company_profile.id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    output_list = []
    
    # Hide applicants if the drive is not approved by admin
    if drive.status != 'Approved':
        return jsonify(output_list), 200

    for app in drive.applications:
        s = app.student
        output_list.append({
            "application_id": app.id,
            "student_name": s.name,
            "email": s.user.email,
            "branch": s.branch,
            "cgpa": s.cgpa,
            "resume_link": s.resume_link,
            "resume_file_path": s.resume_file_path,
            "profile_photo_path": s.profile_photo_path,
            "status": app.status,
            "application_date": app.application_date
        })
    return jsonify(output_list), 200

@company_bp.route('/applications/<int:id>/status', methods=['POST'])
@company_only
def update_app_status(id):
    current_uid = get_jwt_identity()
    u_record = User.query.get(current_uid)
    app = Application.query.get_or_404(id)
    
    if app.drive.company_id != u_record.company_profile.id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    data = request.json
    status = data.get('status')
    if status in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        app.status = status
        db.session.commit()
        return jsonify({"msg": "Status updated"}), 200
    return jsonify({"msg": "Invalid status"}), 400


