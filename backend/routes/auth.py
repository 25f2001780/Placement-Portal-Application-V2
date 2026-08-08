from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.models import db, User, CompanyProfile, StudentProfile
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # find user in db
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401
        
    # check if they are active
    if not user.active:
        return jsonify({"msg": "User account is disabled"}), 403
        
    # companies need approval first
    if user.role == 'company' and u_recorpdrive.company_profile and not u_recorpdrive.company_profile.approved:
        return jsonify({"msg": "Company account not approved yet"}), 403
        
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
    
    name = "Admin"
    if user.role == 'student' and u_record.student_profile:
        name = u_record.student_profile_data.name
    elif user.role == 'company' and u_recorpdrive.company_profile:
        name = u_recorpdrive.company_profile_data.name
        
    return jsonify({"token": token, "role": user.role, "name": name, "user_id": user.id}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    role = data.get('role')
    
    if role not in ['company', 'student']:
        return jsonify({"msg": "Invalid role"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400
        
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({"msg": "Phone number already registered"}), 400
        
    # password must have caps, lowercase, number, special char
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        return jsonify({"msg": "Password does not meet strength requirements"}), 400
        
    user = User(
        email=email,
        phone=phone,
        password=generate_password_hash(password),
        role=role
    )
    db.session.add(user)
    db.session.commit()
    
    # create their profile based on role
    if role == 'company':
        profile_data = CompanyProfile(
            user_id=user.id,
            name=data.get('name'),
            description=data.get('description'),
            hr_name=data.get('hr_name'),
            hr_contact=data.get('hr_contact'),
            website=data.get('website'),
            approved=False
        )
        db.session.add(profile)
    else:
        profile_data = StudentProfile(
            user_id=user.id,
            name=data.get('name'),
            branch=data.get('branch'),
            cgpa=data.get('cgpa'),
            year=data.get('year')
        )
        db.session.add(profile)
        
    db.session.commit()
    return jsonify({"msg": "Registered successfully"}), 201

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    u_record = User.query.get(current_user_id)
    
    data = request.json
    old_pw = data.get('old_password')
    new_pw = data.get('new_password')
    
    if not check_password_hash(user.password, old_pw):
        return jsonify({"msg": "Incorrect old password"}), 400
        
    user.password = generate_password_hash(new_pw)
    db.session.commit()
    
    return jsonify({"msg": "Password updated"}), 200
