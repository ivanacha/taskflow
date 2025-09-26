# Import all models to ensure they are registered with SQLAlchemy
from .user import User, Role, UserRole
from .project import Project, ProjectMember
from .task import Task, TaskDependency
from .activity_log import ActivityLog

__all__ = [
    'User', 'Role', 'UserRole',
    'Project', 'ProjectMember',
    'Task', 'TaskDependency',
    'ActivityLog'
]