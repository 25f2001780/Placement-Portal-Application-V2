from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application
from functools import wraps
from extensions import cache
import os
import json

admin_bp = Blueprint('admin', __name__)
    
def admin_only(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/stats', methods=['GET'])
@admin_only
def get_stats():
    # get cache directly

    cached_data = cache.get('admin_stats') if cache else None
    if cached_data:
        return jsonify(cached_data), 200

    # count everything for the dashboard
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    approved_companies = CompanyProfile.query.filter_by(approved=True).count()
    total_placements = PlacementDrive.query.count()
    approved_placements = PlacementDrive.query.filter_by(status='Approved').count()
    total_applications = Application.query.count()
    selected_students = Application.query.filter_by(status='Selected').count()
    res = {
        "total_students": total_students,
        "total_companies": total_companies,
        "approved_companies": approved_companies,
        "total_drives": total_placements,
        "approved_drives": approved_placements,
        "total_applications": total_applications,
        "selected_students": selected_students
    }

    if cache:
        cache.set('admin_stats', res, timeout=120)

    return jsonify(res), 200

@admin_bp.route('/companies', methods=['GET'])
@admin_only
def get_companies():

    cached = cache.get('admin_companies') if cache else None
    if cached:
        return jsonify(cached), 200

    companies = CompanyProfile.query.all()
    output_list = []
    # loop through companies
    for c in companies:
        output_list.append({
            "id": c.id,
            "user_id": c.user_id,
            "name": c.name,
            "hr_name": c.hr_name,
            "hr_contact": c.hr_contact,
            "website": c.website,
            "logo_path": c.logo_path,
            "approved": c.approved,
            "active": c.user.active,
            "email": c.user.email,
            "phone": c.user.phone
        })

    if cache:
        cache.set('admin_companies', output_list, timeout=120)

    return jsonify(output_list), 200

@admin_bp.route('/companies/<int:id>/approve', methods=['POST'])
@admin_only
def approve_company(id):
    company = CompanyProfile.query.get_or_404(id)
    company.approved = True
    db.session.commit()
    
    # clear cache inline

    if cache:
        for k in ['admin_stats', 'admin_companies', 'admin_students', 'admin_drives', 'admin_analytics']:
            cache.delete(k)
            
    return jsonify({"msg": "Approved"}), 200

@admin_bp.route('/companies/<int:id>/reject', methods=['POST'])
@admin_only
def reject_company(id):
    company = CompanyProfile.query.get_or_404(id)
    user = company.user
    db.session.delete(user)
    db.session.commit()
    
    # clear cache inline

    if cache:
        for k in ['admin_stats', 'admin_companies', 'admin_students', 'admin_drives', 'admin_analytics']:
            cache.delete(k)
            
    return jsonify({"msg": "Rejected and deleted"}), 200

@admin_bp.route('/students', methods=['GET'])
@admin_only
def get_students():

    cached = cache.get('admin_students') if cache else None
    if cached:
        return jsonify(cached), 200

    # get all students
    students = StudentProfile.query.all()
    output_list = []
    for s in students:
        output_list.append({
            "id": s.id,
            "user_id": s.user_id,
            "name": s.name,
            "active": s.user.active,
            "email": s.user.email,
            "phone": s.user.phone,
            "branch": s.branch,
            "cgpa": s.cgpa,
            "year": s.year,
            "profile_photo_path": s.profile_photo_path,
            "resume_file_path": s.resume_file_path,
            "resume_link": s.resume_link
        })

    if cache:
        cache.set('admin_students', output_list, timeout=120)

    return jsonify(output_list), 200

@admin_bp.route('/drives', methods=['GET'])
@admin_only
def load_all_drives():

    cached = cache.get('admin_drives') if cache else None
    if cached:
        return jsonify(cached), 200

    placements = PlacementDrive.query.all()
    output_list = []
    for pdrive in placements:
        output_list.append({
            "id": pdrive.id,
            "job_title": pdrive.job_title,
            "company_name": pdrive.company.name,
            "company_logo": pdrive.company.logo_path,
            "description": pdrive.description,
            "location": pdrive.location,
            "branch_eligibility": pdrive.branch_eligibility,
            "cgpa_cutoff": pdrive.cgpa_cutoff,
            "package_lpa": pdrive.package_lpa,
            "application_deadline": pdrive.application_deadline.strftime('%Y-%m-%d') if pdrive.application_deadline else None,
            "status": pdrive.status,
            "applicant_count": len(pdrive.applications)
        })

    if cache:
        cache.set('admin_drives', output_list, timeout=120)

    return jsonify(output_list), 200

@admin_bp.route('/drives/<int:id>/approve', methods=['POST'])
@admin_only
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    
    # clear cache inline

    if cache:
        for k in ['admin_stats', 'admin_companies', 'admin_students', 'admin_drives', 'admin_analytics']:
            cache.delete(k)
            
    return jsonify({"msg": "Approved"}), 200

@admin_bp.route('/drives/<int:id>/unapprove', methods=['POST'])
@admin_only
def unapprove_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Pending'
    db.session.commit()
    

    if cache:
        for k in ['admin_stats', 'admin_companies', 'admin_students', 'admin_drives', 'admin_analytics']:
            cache.delete(k)
            
    return jsonify({"msg": "Unapproved (Set to Pending)"}), 200

@admin_bp.route('/drives/<int:id>/reject', methods=['POST'])
@admin_only
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Rejected'
    db.session.commit()
    

    if cache:
        for k in ['admin_stats', 'admin_companies', 'admin_students', 'admin_drives', 'admin_analytics']:
            cache.delete(k)
            
    return jsonify({"msg": "Rejected"}), 200

@admin_bp.route('/users/<int:id>/toggle', methods=['POST'])
@admin_only
def toggle_user(id):
    u_record = User.query.get_or_404(id)
    if u_record.role == 'admin':
        return jsonify({"msg": "Cannot toggle admin"}), 400
    u_record.active = not u_record.active
    db.session.commit()

    if cache:
        for k in ['admin_stats', 'admin_companies', 'admin_students', 'admin_drives', 'admin_analytics']:
            cache.delete(k)

    return jsonify({"msg": f"User active status is now {u_record.active}"}), 200

@admin_bp.route('/drives/<int:id>/applications', methods=['GET'])
@admin_only
def get_applications(id):
    drive = PlacementDrive.query.get_or_404(id)
    output_list = []
    for app in drive.applications:
        student = app.student
        output_list.append({
            "application_id": app.id,
            "student_name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "resume_link": student.resume_link,
            "resume_file_path": student.resume_file_path,
            "profile_photo_path": student.profile_photo_path,
            "status": app.status,
            "application_date": app.application_date.strftime('%Y-%m-%d')
        })
    return jsonify(output_list), 200

# for chartjs on the dashboard
@admin_bp.route('/analytics', methods=['GET'])
@admin_only
def get_analytics():

    cached = cache.get('admin_analytics') if cache else None
    if cached:
        return jsonify(cached), 200

    students = StudentProfile.query.all()
    branch_app_counts = {}
    for s in students:
        branch = s.branch or 'Unknown'
        app_count = Application.query.filter_by(student_id=s.id).count()
        branch_app_counts[branch] = branch_app_counts.get(branch, 0) + app_count

    drive_statuses = {'Approved': 0, 'Pending': 0, 'Rejected': 0}
    placements = PlacementDrive.query.all()
    for pdrive in placements:
        if pdrive.status in drive_statuses:
            drive_statuses[pdrive.status] += 1

    company_apps = {}
    for pdrive in placements:
        name = pdrive.company.name
        count = len(pdrive.applications)
        company_apps[name] = company_apps.get(name, 0) + count

    total_apps = Application.query.count()
    selected_apps = Application.query.filter_by(status='Selected').count()
    shortlisted_apps = Application.query.filter_by(status='Shortlisted').count()
    rejected_apps = Application.query.filter_by(status='Rejected').count()
    applied_apps = Application.query.filter_by(status='Applied').count()

    res = {
        "branch_applications": {
            "labels": list(branch_app_counts.keys()),
            "data": list(branch_app_counts.values())
        },
        "drive_status": {
            "labels": list(drive_statuses.keys()),
            "data": list(drive_statuses.values())
        },
        "company_recruitment": {
            "labels": list(company_apps.keys()),
            "data": list(company_apps.values())
        },
        "application_status": {
            "labels": ["Applied", "Shortlisted", "Selected", "Rejected"],
            "data": [applied_apps, shortlisted_apps, selected_apps, rejected_apps]
        }
    }

    if cache:
        cache.set('admin_analytics', res, timeout=120)

    return jsonify(res), 200

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_only
def manage_settings():
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    settings_path = os.path.join(BASE_DIR, 'settings.json')
    
    if request.method == 'POST':
        data = request.json
        with open(settings_path, 'w') as f:
            json.dump(data, f)
        return jsonify({"msg": "Settings saved successfully"}), 200
        
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            return jsonify(json.load(f)), 200
    return jsonify({}), 200

@admin_bp.route('/trigger-report', methods=['POST'])
@admin_only
def trigger_report():
    from tasks.celery_tasks import monthly_report
    monthly_report.delay()
    return jsonify({"msg": "Monthly report triggered successfully"}), 200

@admin_bp.route('/trigger-reminders', methods=['POST'])
@admin_only
def trigger_reminders():
    from tasks.celery_tasks import daily_reminders
    daily_reminders.delay(force=True)
    return jsonify({"msg": "Student reminders triggered successfully"}), 200
