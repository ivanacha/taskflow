#!/bin/bash

set -e  # Exit on any error

echo "🗄️  Setting up Database..."

# Load environment variables if .env exists
if [ -f "$(dirname "$0")/../.env" ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat "$(dirname "$0")/../.env" | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found. Using default values..."
    export DB_HOST=${DB_HOST:-localhost}
    export DB_PORT=${DB_PORT:-5432}
    export DB_NAME=${DB_NAME:-taskflow}
    export DB_USER=${DB_USER:-postgres}
    export DB_PASSWORD=${DB_PASSWORD:-postgres}
fi

echo "🔧 Database configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    # Try to connect to PostgreSQL
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c '\q' 2>/dev/null; then
        echo "✅ PostgreSQL connection successful!"
    else
        echo "❌ Cannot connect to PostgreSQL. Please ensure:"
        echo "  1. PostgreSQL is running"
        echo "  2. Connection details in .env are correct"
        echo "  3. User has proper permissions"

        # If we're in Docker environment, try to start PostgreSQL
        if [ "$DOCKER_ENV" = "true" ] || [ -f "/.dockerenv" ]; then
            echo "🐳 Detected Docker environment. Attempting to start PostgreSQL..."
            if command -v docker-compose &> /dev/null && [ -f "$(dirname "$0")/../docker-compose.dev.yml" ]; then
                cd "$(dirname "$0")/.."
                docker-compose -f docker-compose.dev.yml up -d postgres
                echo "⏳ Waiting for PostgreSQL to be ready..."
                sleep 10
            fi
        else
            echo "💡 To start PostgreSQL:"
            echo "  - macOS: brew services start postgresql"
            echo "  - Ubuntu: sudo systemctl start postgresql"
            echo "  - Docker: docker-compose -f docker-compose.dev.yml up -d postgres"
            exit 1
        fi
    fi
else
    echo "⚠️  psql not found. Installing PostgreSQL client..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y postgresql-client
    elif command -v brew &> /dev/null; then
        brew install postgresql
    else
        echo "❌ Cannot install PostgreSQL client automatically."
        echo "Please install it manually and run this script again."
        exit 1
    fi
fi

# Create database if it doesn't exist
echo "🏗️  Creating database if it doesn't exist..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "📋 Database $DB_NAME already exists or creation failed"

# Test database connection
echo "🧪 Testing database connection..."
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; then
    echo "✅ Database connection successful!"
else
    echo "❌ Failed to connect to database $DB_NAME"
    exit 1
fi

# Run migrations if backend exists and has migration files
BACKEND_DIR="$(dirname "$0")/../backend"
if [ -d "$BACKEND_DIR" ]; then
    cd "$BACKEND_DIR"

    # Check for Django migrations
    if [ -f "manage.py" ]; then
        echo "🔄 Running Django migrations..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        python manage.py makemigrations || echo "⚠️  No new migrations to create"
        python manage.py migrate || echo "⚠️  Migration failed"
    fi

    # Check for Alembic migrations (FastAPI)
    if [ -f "alembic.ini" ]; then
        echo "🔄 Running Alembic migrations..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        alembic upgrade head || echo "⚠️  Alembic migration failed"
    fi

    # If no migration system found, check for SQL files
    if [ -d "../database" ]; then
        echo "🔄 Looking for SQL initialization files..."
        for sql_file in ../database/*.sql; do
            if [ -f "$sql_file" ]; then
                echo "📝 Executing $sql_file..."
                PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$sql_file"
            fi
        done
    fi
fi

echo "🎉 Database setup complete!"
echo ""
echo "🔧 Database connection string:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"