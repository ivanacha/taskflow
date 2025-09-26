#!/usr/bin/env python3
"""
Database setup script for TaskFlow
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def test_connection():
    """Test basic PostgreSQL connectivity"""
    try:
        # Try to connect to postgres database (default)
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres"
        )
        print("✅ Connected to PostgreSQL successfully!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def setup_database():
    """Set up the TaskFlow database and user"""
    try:
        # Connect to PostgreSQL as superuser
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create user if not exists
        try:
            cursor.execute("CREATE USER taskflow_user WITH PASSWORD 'taskflow_password';")
            print("✅ Created taskflow_user")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️  User taskflow_user already exists")

        # Create database if not exists
        try:
            cursor.execute("CREATE DATABASE taskflow_db OWNER taskflow_user;")
            print("✅ Created taskflow_db")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️  Database taskflow_db already exists")

        # Grant privileges
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE taskflow_db TO taskflow_user;")
        print("✅ Granted privileges to taskflow_user")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def apply_schema():
    """Apply the schema to the TaskFlow database"""
    try:
        # Connect to the TaskFlow database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="taskflow_db",
            user="taskflow_user",
            password="taskflow_password"
        )
        cursor = conn.cursor()

        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Applied schema successfully!")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Schema application failed: {e}")
        return False

def test_taskflow_connection():
    """Test connection to TaskFlow database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="taskflow_db",
            user="taskflow_user",
            password="taskflow_password"
        )
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        print(f"✅ TaskFlow database ready! Found {count} users.")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ TaskFlow database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🐘 PostgreSQL Database Setup for TaskFlow")
    print("=" * 50)

    print("\n1. Testing basic connectivity...")
    if not test_connection():
        print("Cannot connect to PostgreSQL. Please ensure it's running.")
        sys.exit(1)

    print("\n2. Setting up database and user...")
    if not setup_database():
        print("Failed to setup database.")
        sys.exit(1)

    print("\n3. Applying schema...")
    if not apply_schema():
        print("Failed to apply schema.")
        sys.exit(1)

    print("\n4. Testing TaskFlow database...")
    if not test_taskflow_connection():
        print("TaskFlow database test failed.")
        sys.exit(1)

    print("\n🎉 Database setup completed successfully!")
    print("\nConnection details:")
    print("  Host: localhost")
    print("  Port: 5432")
    print("  Database: taskflow_db")
    print("  User: taskflow_user")
    print("  Password: taskflow_password")