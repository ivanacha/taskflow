from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.api import bp
from app.models import User, ActivityLog
from app import db

@bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']) and user.is_active:
        access_token = create_access_token(identity=str(user.id))

        # Update last login
        user.last_login_at = db.func.now()

        # Log the login activity
        ActivityLog.log_user_action(
            user_id=user.id,
            action_type='user_login',
            description=f'User {user.username} logged in'
        )

        db.session.commit()

        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()

    required_fields = ['username', 'email', 'password']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Username, email, and password required'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409

    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Log the registration activity
    ActivityLog.log_user_action(
        user_id=user.id,
        action_type='user_created',
        description=f'New user {user.username} registered'
    )

    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }), 201

@bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200