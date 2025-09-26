from flask import jsonify
from flask_jwt_extended import jwt_required
from app.api import bp
from app.models import Task

@bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks"""
    tasks = Task.query.all()
    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    }), 200

@bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get task by ID"""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    return jsonify({'task': task.to_dict(include_dependencies=True)}), 200