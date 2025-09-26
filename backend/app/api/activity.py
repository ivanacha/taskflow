from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.api import bp
from app.models import ActivityLog

@bp.route('/activity', methods=['GET'])
@jwt_required()
def get_activity():
    """Get activity logs with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    project_id = request.args.get('project_id')
    task_id = request.args.get('task_id')
    user_id = request.args.get('user_id')

    query = ActivityLog.query

    if project_id:
        query = query.filter_by(project_id=project_id)
    if task_id:
        query = query.filter_by(task_id=task_id)
    if user_id:
        query = query.filter_by(user_id=user_id)

    activity_logs = query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'activity_logs': [log.to_dict() for log in activity_logs.items],
        'total': activity_logs.total,
        'pages': activity_logs.pages,
        'current_page': page
    }), 200