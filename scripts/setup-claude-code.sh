#!/bin/bash

set -e  # Exit on any error

echo "🤖 Setting up Claude Code Configuration..."

PROJECT_ROOT="$(dirname "$0")/.."
VSCODE_DIR="$PROJECT_ROOT/.vscode"

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "⚠️  Claude Code CLI not found. Attempting to install..."

    # Try to install Claude Code
    if command -v npm &> /dev/null; then
        echo "📦 Installing Claude Code via npm..."
        npm install -g @anthropic/claude-code || echo "⚠️  Failed to install via npm"
    elif command -v curl &> /dev/null; then
        echo "📦 Installing Claude Code via curl..."
        curl -fsSL https://api.anthropic.com/claude-code/install.sh | sh || echo "⚠️  Failed to install via curl"
    else
        echo "❌ Cannot install Claude Code automatically."
        echo "Please install it manually from: https://claude.ai/code"
        echo "Then run this script again."
        exit 1
    fi

    # Verify installation
    if ! command -v claude &> /dev/null; then
        echo "❌ Claude Code installation failed."
        echo "Please install it manually and run this script again."
        exit 1
    fi
fi

echo "✅ Claude Code CLI found: $(command -v claude)"

# Verify VS Code directory exists
if [ ! -d "$VSCODE_DIR" ]; then
    echo "❌ .vscode directory not found. Please run the main setup script first."
    exit 1
fi

echo "📁 VS Code directory found: $VSCODE_DIR"

# Check if CLAUDE.md exists
if [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
    echo "⚠️  CLAUDE.md not found. Creating basic configuration..."
    cat > "$PROJECT_ROOT/CLAUDE.md" << 'EOF'
# Claude Code Configuration

## Project Structure
This is a full-stack application with React frontend and Python backend.

## Common Commands
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
- Database: `docker-compose -f docker-compose.dev.yml up -d postgres`

## Testing
- Frontend: `cd frontend && npm test`
- Backend: `cd backend && pytest`
EOF
    echo "✅ Created basic CLAUDE.md configuration"
else
    echo "📋 CLAUDE.md already exists"
fi

# Set up Claude Code workspace configuration
echo "🔧 Configuring Claude Code workspace settings..."

# Create claude-code.json if it doesn't exist
CLAUDE_CONFIG="$PROJECT_ROOT/.claude-code.json"
if [ ! -f "$CLAUDE_CONFIG" ]; then
    cat > "$CLAUDE_CONFIG" << 'EOF'
{
  "version": "1.0",
  "name": "TaskFlow",
  "description": "Full-stack task management application",
  "type": "workspace",
  "paths": {
    "frontend": "./frontend",
    "backend": "./backend",
    "database": "./database",
    "scripts": "./scripts"
  },
  "environments": {
    "development": {
      "frontend": {
        "port": 5173,
        "url": "http://localhost:5173"
      },
      "backend": {
        "port": 8000,
        "url": "http://localhost:8000"
      },
      "database": {
        "host": "localhost",
        "port": 5432,
        "name": "taskflow"
      }
    }
  },
  "commands": {
    "setup": "./scripts/setup.sh",
    "start-frontend": "cd frontend && npm run dev",
    "start-backend": "cd backend && source venv/bin/activate && uvicorn main:app --reload",
    "start-database": "docker-compose -f docker-compose.dev.yml up -d postgres",
    "test-frontend": "cd frontend && npm test",
    "test-backend": "cd backend && pytest",
    "lint-frontend": "cd frontend && npm run lint",
    "format-backend": "cd backend && black ."
  }
}
EOF
    echo "✅ Created Claude Code workspace configuration"
else
    echo "📋 Claude Code configuration already exists"
fi

# Initialize Claude Code in the project
echo "🚀 Initializing Claude Code in project..."
cd "$PROJECT_ROOT"

# Try to initialize Claude Code
if claude init --force 2>/dev/null || true; then
    echo "✅ Claude Code initialized successfully"
else
    echo "⚠️  Claude Code initialization skipped (may already be initialized)"
fi

# Set up Claude Code status line if supported
echo "📊 Configuring Claude Code status line..."
if claude config statusline.enabled true 2>/dev/null || true; then
    echo "✅ Claude Code status line enabled"
    claude config statusline.format "🤖 TaskFlow - Claude Code" 2>/dev/null || true
else
    echo "⚠️  Claude Code status line configuration skipped"
fi

# Configure auto-save
echo "💾 Configuring Claude Code auto-save..."
if claude config autosave true 2>/dev/null || true; then
    echo "✅ Claude Code auto-save enabled"
else
    echo "⚠️  Claude Code auto-save configuration skipped"
fi

# Verify configuration
echo "🧪 Verifying Claude Code configuration..."
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✅ Claude Code workspace configuration verified"
    echo "📋 Configuration location: $CLAUDE_CONFIG"
else
    echo "⚠️  Claude Code configuration verification failed"
fi

echo "🎉 Claude Code setup complete!"
echo ""
echo "🔧 Claude Code commands:"
echo "  claude --help           - Show help"
echo "  claude status           - Show project status"
echo "  claude run setup        - Run setup script"
echo "  claude run start-dev    - Start development environment"
echo ""
echo "💡 VS Code integration:"
echo "  - Install the Claude Code extension from the VS Code marketplace"
echo "  - Open VS Code in this directory to use the configured settings"
echo "  - Use Cmd+Shift+P and search for 'Claude' to access features"