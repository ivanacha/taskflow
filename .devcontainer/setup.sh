#!/bin/bash

echo "🚀 Setting up TaskFlow development environment..."

# Set up backend
if [ -d "backend" ]; then
    echo "📦 Setting up Python backend..."
    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python -m venv venv
    fi

    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo "✅ Backend dependencies installed"
    else
        echo "⚠️ No requirements.txt found for backend"
    fi

    cd ..
fi

# Set up frontend
if [ -d "frontend" ]; then
    echo "📦 Setting up React frontend..."
    cd frontend

    if [ -f "package.json" ]; then
        npm install
        echo "✅ Frontend dependencies installed"
    else
        echo "⚠️ No package.json found for frontend"
    fi

    cd ..
fi

# Set up database initialization
if [ -d "database" ]; then
    echo "🗄️ Setting up database..."

    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL to be ready..."
    until pg_isready -h postgres -p 5432 -U taskflow_user; do
        sleep 2
    done

    echo "✅ Database setup complete"
fi

# Install Claude Code
echo "🤖 Installing Claude Code..."
if command -v npm &> /dev/null; then
    npm install -g @anthropic-ai/claude-code
    echo "✅ Claude Code installed globally"
else
    echo "⚠️ npm not found, skipping Claude Code installation"
fi

# Set up git hooks
if [ -d ".git" ]; then
    echo "🔧 Setting up git hooks..."

    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks..."

# Check if backend code exists and run linting
if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
    cd backend
    source venv/bin/activate 2>/dev/null || true

    # Run Python linting
    if command -v black &> /dev/null; then
        echo "Running black formatter..."
        black --check . || exit 1
    fi

    if command -v flake8 &> /dev/null; then
        echo "Running flake8 linter..."
        flake8 . || exit 1
    fi

    cd ..
fi

# Check if frontend code exists and run linting
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend

    # Run ESLint
    if npm list eslint &> /dev/null; then
        echo "Running ESLint..."
        npm run lint || exit 1
    fi

    # Run TypeScript check
    if npm list typescript &> /dev/null; then
        echo "Running TypeScript check..."
        npx tsc --noEmit || exit 1
    fi

    cd ..
fi

echo "✅ Pre-commit checks passed"
EOF

    chmod +x .git/hooks/pre-commit
    echo "✅ Git hooks installed"
fi

# Create helpful scripts
echo "📝 Creating development scripts..."

# Create start script
cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting TaskFlow development environment..."

# Start all services
docker-compose -f docker-compose.dev.yml up -d

echo "✅ Development environment started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "🗄️ Database: localhost:5432"
echo "🔴 Redis: localhost:6379"
echo "🔧 PgAdmin: http://localhost:8080"
echo ""
echo "To view logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "To stop: docker-compose -f docker-compose.dev.yml down"
EOF

chmod +x start-dev.sh

# Create stop script
cat > stop-dev.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping TaskFlow development environment..."
docker-compose -f docker-compose.dev.yml down
echo "✅ Development environment stopped!"
EOF

chmod +x stop-dev.sh

# Create reset script
cat > reset-dev.sh << 'EOF'
#!/bin/bash
echo "🔄 Resetting TaskFlow development environment..."
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
echo "✅ Development environment reset!"
EOF

chmod +x reset-dev.sh

echo ""
echo "🎉 TaskFlow development environment setup complete!"
echo ""
echo "🚀 Quick start commands:"
echo "  ./start-dev.sh    - Start the development environment"
echo "  ./stop-dev.sh     - Stop the development environment"
echo "  ./reset-dev.sh    - Reset and rebuild everything"
echo ""
echo "📚 Available services:"
echo "  Frontend (React): http://localhost:3000"
echo "  Backend (Flask):  http://localhost:5000"
echo "  PostgreSQL:       localhost:5432"
echo "  Redis:            localhost:6379"
echo "  PgAdmin:          http://localhost:8080"
echo ""
echo "Happy coding! 🎯"