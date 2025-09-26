#!/usr/bin/env python3
"""
TaskFlow Backend Application

A Flask-based REST API for task and project management.
"""

import os
from app import create_app, db
from app.models import User, Role, UserRole, Project, ProjectMember, Task, TaskDependency, ActivityLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'UserRole': UserRole,
        'Project': Project,
        'ProjectMember': ProjectMember,
        'Task': Task,
        'TaskDependency': TaskDependency,
        'ActivityLog': ActivityLog
    }

@app.cli.command()
def init_db():
    """Initialize the database with default data."""
    db.create_all()

    # Create default roles
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(
            name='admin',
            description='Administrator with full access',
            permissions={
                'users': ['create', 'read', 'update', 'delete'],
                'projects': ['create', 'read', 'update', 'delete'],
                'tasks': ['create', 'read', 'update', 'delete'],
                'roles': ['create', 'read', 'update', 'delete']
            }
        )
        db.session.add(admin_role)

    manager_role = Role.query.filter_by(name='manager').first()
    if not manager_role:
        manager_role = Role(
            name='manager',
            description='Project manager with project management access',
            permissions={
                'projects': ['create', 'read', 'update'],
                'tasks': ['create', 'read', 'update', 'delete'],
                'users': ['read']
            }
        )
        db.session.add(manager_role)

    member_role = Role.query.filter_by(name='member').first()
    if not member_role:
        member_role = Role(
            name='member',
            description='Team member with task access',
            permissions={
                'projects': ['read'],
                'tasks': ['read', 'update'],
                'users': ['read']
            }
        )
        db.session.add(member_role)

    db.session.commit()
    print("Database initialized with default roles.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)