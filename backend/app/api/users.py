from flask import jsonify
from flask_jwt_extended import jwt_required
from app.api import bp
from app.models import User

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users"""
    users = User.query.filter_by(is_active=True).all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200