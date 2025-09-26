from datetime import datetime
from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSON
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)

    # Relationships
    user_roles = db.relationship('UserRole', back_populates='user', lazy='dynamic')
    created_projects = db.relationship('Project', foreign_keys='Project.created_by', back_populates='creator', lazy='dynamic')
    project_memberships = db.relationship('ProjectMember', back_populates='user', lazy='dynamic')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', back_populates='assignee', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', back_populates='creator', lazy='dynamic')
    activity_logs = db.relationship('ActivityLog', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_roles(self):
        return [ur.role for ur in self.user_roles if ur.role]

    def has_role(self, role_name):
        return any(ur.role.name == role_name for ur in self.user_roles if ur.role)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'roles': [role.name for role in self.get_roles()]
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_roles = db.relationship('UserRole', back_populates='role', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(db.Model):
    __tablename__ = 'user_roles'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))

    # Relationships
    user = db.relationship('User', back_populates='user_roles')
    role = db.relationship('Role', back_populates='user_roles')
    assigner = db.relationship('User', foreign_keys=[assigned_by])

    def to_dict(self):
        return {
            'user_id': str(self.user_id),
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'assigned_at': self.assigned_at.isoformat(),
            'assigned_by': str(self.assigned_by) if self.assigned_by else None
        }

    def __repr__(self):
        return f'<UserRole {self.user_id}-{self.role_id}>'