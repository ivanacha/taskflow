#!/bin/bash

set -e  # Exit on any error

echo "🚀 Setting up Frontend Dependencies..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Node.js version: $(node --version)"
echo "📦 npm version: $(npm --version)"

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend" || exit 1

echo "📁 Working directory: $(pwd)"

# Install dependencies
echo "⬇️  Installing frontend dependencies..."
npm install

# Verify installation
if [ -d "node_modules" ]; then
    echo "✅ Frontend dependencies installed successfully!"
    echo "📊 Installed packages:"
    npm list --depth=0 | head -10
else
    echo "❌ Failed to install frontend dependencies!"
    exit 1
fi

echo "🎉 Frontend setup complete!"
echo ""
echo "🔧 Available commands:"
echo "  npm run dev      - Start development server"
echo "  npm run build    - Build for production"
echo "  npm run test     - Run tests"
echo "  npm run lint     - Run linter"