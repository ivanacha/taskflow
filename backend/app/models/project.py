from datetime import datetime
from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='created_projects')
    members = db.relationship('ProjectMember', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='project', lazy='dynamic', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', back_populates='project', lazy='dynamic')

    # Define valid statuses
    VALID_STATUSES = ['active', 'completed', 'archived', 'on_hold']

    def get_members(self):
        return [pm.user for pm in self.members if pm.is_active]

    def get_member_role(self, user_id):
        member = self.members.filter_by(user_id=user_id, is_active=True).first()
        return member.role if member else None

    def is_member(self, user_id):
        return self.members.filter_by(user_id=user_id, is_active=True).first() is not None

    def add_member(self, user_id, role='member'):
        existing = self.members.filter_by(user_id=user_id).first()
        if existing:
            existing.is_active = True
            existing.role = role
            existing.joined_at = datetime.utcnow()
        else:
            member = ProjectMember(
                project_id=self.id,
                user_id=user_id,
                role=role
            )
            db.session.add(member)

    def remove_member(self, user_id):
        member = self.members.filter_by(user_id=user_id).first()
        if member:
            member.is_active = False

    def get_task_counts(self):
        from .task import Task
        return {
            'total': self.tasks.count(),
            'todo': self.tasks.filter_by(status='todo').count(),
            'in_progress': self.tasks.filter_by(status='in_progress').count(),
            'review': self.tasks.filter_by(status='review').count(),
            'completed': self.tasks.filter_by(status='completed').count()
        }

    def to_dict(self, include_members=False, include_tasks=False):
        data = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': str(self.created_by),
            'creator_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'task_counts': self.get_task_counts()
        }

        if include_members:
            data['members'] = [pm.to_dict() for pm in self.members if pm.is_active]

        if include_tasks:
            data['tasks'] = [task.to_dict() for task in self.tasks]

        return data

    def __repr__(self):
        return f'<Project {self.name}>'


class ProjectMember(db.Model):
    __tablename__ = 'project_members'

    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    role = db.Column(db.String(20), default='member', nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    project = db.relationship('Project', back_populates='members')
    user = db.relationship('User', back_populates='project_memberships')

    # Define valid roles
    VALID_ROLES = ['owner', 'manager', 'member', 'viewer']

    def to_dict(self):
        return {
            'project_id': str(self.project_id),
            'user_id': str(self.user_id),
            'user_name': self.user.full_name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'role': self.role,
            'joined_at': self.joined_at.isoformat(),
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<ProjectMember {self.project_id}-{self.user_id}>'