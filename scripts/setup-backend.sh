#!/bin/bash

set -e  # Exit on any error

echo "🐍 Setting up Backend Dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "📦 Python version: $(python3 --version)"

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

echo "📁 Working directory: $(pwd)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔨 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "📋 Virtual environment already exists!"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "⬇️  Installing Python dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "✅ Python dependencies installed successfully!"
else
    echo "⚠️  requirements.txt not found. Installing common FastAPI dependencies..."
    pip install fastapi uvicorn python-dotenv sqlalchemy psycopg2-binary alembic pytest black flake8 mypy

    # Create requirements.txt
    echo "📝 Creating requirements.txt..."
    pip freeze > requirements.txt
    echo "✅ Created requirements.txt with installed packages!"
fi

# Check if we can import key packages
echo "🧪 Verifying installation..."
python3 -c "import fastapi; print('✅ FastAPI imported successfully')" || echo "⚠️  FastAPI not available"
python3 -c "import uvicorn; print('✅ Uvicorn imported successfully')" || echo "⚠️  Uvicorn not available"

echo "🎉 Backend setup complete!"
echo ""
echo "🔧 To activate the virtual environment manually:"
echo "  source backend/venv/bin/activate"
echo ""
echo "🔧 Available commands (after activation):"
echo "  uvicorn main:app --reload    - Start FastAPI server"
echo "  python manage.py runserver   - Start Django server (if using Django)"
echo "  pytest                       - Run tests"
echo "  black .                      - Format code"
echo "  flake8 .                     - Lint code"