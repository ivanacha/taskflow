from datetime import datetime
from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSON

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'))
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'))
    action_type = db.Column(db.String(50), nullable=False)
    changes = db.Column(JSON)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='activity_logs')
    project = db.relationship('Project', back_populates='activity_logs')
    task = db.relationship('Task', back_populates='activity_logs')

    # Define valid action types
    VALID_ACTION_TYPES = [
        # User actions
        'user_created', 'user_updated', 'user_login', 'user_logout',
        # Project actions
        'project_created', 'project_updated', 'project_deleted',
        'project_member_added', 'project_member_removed', 'project_member_role_changed',
        # Task actions
        'task_created', 'task_updated', 'task_deleted', 'task_assigned', 'task_unassigned',
        'task_status_changed', 'task_priority_changed', 'task_completed',
        'task_dependency_added', 'task_dependency_removed',
        # File actions
        'file_uploaded', 'file_downloaded', 'file_deleted',
        # Comment actions
        'comment_added', 'comment_updated', 'comment_deleted',
        # General actions
        'view', 'export', 'import'
    ]

    @classmethod
    def log_action(cls, user_id, action_type, description, project_id=None, task_id=None, changes=None):
        """Convenience method to create activity log entries"""
        activity = cls(
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            action_type=action_type,
            description=description,
            changes=changes
        )
        db.session.add(activity)
        return activity

    @classmethod
    def log_user_action(cls, user_id, action_type, description, changes=None):
        """Log user-related actions"""
        return cls.log_action(user_id, action_type, description, changes=changes)

    @classmethod
    def log_project_action(cls, user_id, project_id, action_type, description, changes=None):
        """Log project-related actions"""
        return cls.log_action(user_id, action_type, description, project_id=project_id, changes=changes)

    @classmethod
    def log_task_action(cls, user_id, task_id, action_type, description, project_id=None, changes=None):
        """Log task-related actions"""
        return cls.log_action(user_id, action_type, description, project_id=project_id, task_id=task_id, changes=changes)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'user_name': self.user.full_name if self.user else None,
            'project_id': str(self.project_id) if self.project_id else None,
            'project_name': self.project.name if self.project else None,
            'task_id': str(self.task_id) if self.task_id else None,
            'task_title': self.task.title if self.task else None,
            'action_type': self.action_type,
            'description': self.description,
            'changes': self.changes,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<ActivityLog {self.action_type} by {self.user_id}>'