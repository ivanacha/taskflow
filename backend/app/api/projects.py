from flask import jsonify
from flask_jwt_extended import jwt_required
from app.api import bp
from app.models import Project

@bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all projects"""
    projects = Project.query.all()
    return jsonify({
        'projects': [project.to_dict() for project in projects]
    }), 200

@bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project by ID"""
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    return jsonify({'project': project.to_dict(include_members=True)}), 200