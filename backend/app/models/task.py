from datetime import datetime
from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo', nullable=False)
    priority = db.Column(db.String(10), default='medium', nullable=False)
    category = db.Column(db.String(50))
    estimated_hours = db.Column(db.Integer)
    actual_hours = db.Column(db.Integer)
    due_date = db.Column(db.DateTime)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    # Relationships
    project = db.relationship('Project', back_populates='tasks')
    assignee = db.relationship('User', foreign_keys=[assigned_to], back_populates='assigned_tasks')
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='created_tasks')
    dependencies = db.relationship(
        'TaskDependency',
        foreign_keys='TaskDependency.task_id',
        back_populates='task',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    dependents = db.relationship(
        'TaskDependency',
        foreign_keys='TaskDependency.depends_on_task_id',
        back_populates='depends_on_task',
        lazy='dynamic'
    )
    activity_logs = db.relationship('ActivityLog', back_populates='task', lazy='dynamic')

    # Define valid statuses
    VALID_STATUSES = ['todo', 'in_progress', 'review', 'completed', 'cancelled']

    # Define valid priorities
    VALID_PRIORITIES = ['low', 'medium', 'high', 'urgent']

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = datetime.utcnow()

    def get_dependencies(self):
        """Get tasks that this task depends on"""
        return [dep.depends_on_task for dep in self.dependencies if dep.depends_on_task]

    def get_dependents(self):
        """Get tasks that depend on this task"""
        return [dep.task for dep in self.dependents if dep.task]

    def can_start(self):
        """Check if task can be started (all dependencies are completed)"""
        dependencies = self.get_dependencies()
        return all(dep.status == 'completed' for dep in dependencies)

    def add_dependency(self, depends_on_task_id, dependency_type='blocks'):
        """Add a dependency to another task"""
        # Check for circular dependencies
        if self._would_create_cycle(depends_on_task_id):
            raise ValueError("Adding this dependency would create a circular dependency")

        existing = self.dependencies.filter_by(depends_on_task_id=depends_on_task_id).first()
        if not existing:
            dependency = TaskDependency(
                task_id=self.id,
                depends_on_task_id=depends_on_task_id,
                dependency_type=dependency_type
            )
            db.session.add(dependency)

    def _would_create_cycle(self, depends_on_task_id):
        """Check if adding a dependency would create a circular dependency"""
        visited = set()

        def has_path_to_task(from_task_id, to_task_id):
            if from_task_id == to_task_id:
                return True
            if from_task_id in visited:
                return False

            visited.add(from_task_id)

            # Check all tasks that from_task_id depends on
            dependencies = TaskDependency.query.filter_by(task_id=from_task_id).all()
            for dep in dependencies:
                if has_path_to_task(dep.depends_on_task_id, to_task_id):
                    return True

            return False

        # Check if the task we want to depend on eventually depends on this task
        return has_path_to_task(depends_on_task_id, self.id)

    @property
    def is_overdue(self):
        return self.due_date and self.due_date < datetime.utcnow() and self.status != 'completed'

    def to_dict(self, include_dependencies=False):
        data = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'category': self.category,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'project_id': str(self.project_id),
            'project_name': self.project.name if self.project else None,
            'assigned_to': str(self.assigned_to) if self.assigned_to else None,
            'assignee_name': self.assignee.full_name if self.assignee else None,
            'created_by': str(self.created_by),
            'creator_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_overdue': self.is_overdue,
            'can_start': self.can_start()
        }

        if include_dependencies:
            data['dependencies'] = [dep.to_dict() for dep in self.dependencies]
            data['dependents'] = [dep.to_dict() for dep in self.dependents]

        return data

    def __repr__(self):
        return f'<Task {self.title}>'


class TaskDependency(db.Model):
    __tablename__ = 'task_dependencies'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'), nullable=False)
    depends_on_task_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tasks.id'), nullable=False)
    dependency_type = db.Column(db.String(20), default='blocks', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = db.relationship('Task', foreign_keys=[task_id], back_populates='dependencies')
    depends_on_task = db.relationship('Task', foreign_keys=[depends_on_task_id], back_populates='dependents')

    # Define valid dependency types
    VALID_DEPENDENCY_TYPES = ['blocks', 'relates_to', 'subtask_of']

    # Ensure a task doesn't depend on itself
    __table_args__ = (
        db.CheckConstraint('task_id != depends_on_task_id', name='no_self_dependency'),
        db.UniqueConstraint('task_id', 'depends_on_task_id', name='unique_dependency')
    )

    def to_dict(self):
        return {
            'id': str(self.id),
            'task_id': str(self.task_id),
            'task_title': self.task.title if self.task else None,
            'depends_on_task_id': str(self.depends_on_task_id),
            'depends_on_task_title': self.depends_on_task.title if self.depends_on_task else None,
            'dependency_type': self.dependency_type,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<TaskDependency {self.task_id} -> {self.depends_on_task_id}>'