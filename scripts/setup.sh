#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Main setup function
main() {
    print_header "🚀 TaskFlow Development Environment Setup"
    echo ""
    print_status "This script will set up your complete development environment"
    echo ""

    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    print_status "Project root: $PROJECT_ROOT"
    cd "$PROJECT_ROOT"

    # Check if running in container
    IN_CONTAINER=false
    if [ -f "/.dockerenv" ] || [ "$DOCKER_ENV" = "true" ]; then
        IN_CONTAINER=true
        print_status "Detected container environment"
    fi

    # Parse command line arguments
    SKIP_FRONTEND=false
    SKIP_BACKEND=false
    SKIP_DATABASE=false
    SKIP_CLAUDE=false
    VERBOSE=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-database)
                SKIP_DATABASE=true
                shift
                ;;
            --skip-claude)
                SKIP_CLAUDE=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Show what will be set up
    echo ""
    print_header "📋 Setup Plan:"
    [ "$SKIP_FRONTEND" = false ] && echo "✅ Frontend (React + TypeScript)"
    [ "$SKIP_BACKEND" = false ] && echo "✅ Backend (Python + Virtual Environment)"
    [ "$SKIP_DATABASE" = false ] && echo "✅ Database (PostgreSQL)"
    [ "$SKIP_CLAUDE" = false ] && echo "✅ Claude Code Configuration"
    echo ""

    # Confirm setup
    if [ "$VERBOSE" = false ]; then
        read -p "Continue with setup? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Setup cancelled"
            exit 0
        fi
    fi

    # Frontend setup
    if [ "$SKIP_FRONTEND" = false ]; then
        print_header "🎨 Setting up Frontend..."
        if [ -f "$SCRIPT_DIR/setup-frontend.sh" ]; then
            chmod +x "$SCRIPT_DIR/setup-frontend.sh"
            if "$SCRIPT_DIR/setup-frontend.sh"; then
                print_success "Frontend setup completed"
            else
                print_error "Frontend setup failed"
                exit 1
            fi
        else
            print_warning "Frontend setup script not found"
        fi
        echo ""
    fi

    # Backend setup
    if [ "$SKIP_BACKEND" = false ]; then
        print_header "🐍 Setting up Backend..."
        if [ -f "$SCRIPT_DIR/setup-backend.sh" ]; then
            chmod +x "$SCRIPT_DIR/setup-backend.sh"
            if "$SCRIPT_DIR/setup-backend.sh"; then
                print_success "Backend setup completed"
            else
                print_error "Backend setup failed"
                exit 1
            fi
        else
            print_warning "Backend setup script not found"
        fi
        echo ""
    fi

    # Database setup
    if [ "$SKIP_DATABASE" = false ]; then
        print_header "🗄️  Setting up Database..."
        if [ -f "$SCRIPT_DIR/setup-database.sh" ]; then
            chmod +x "$SCRIPT_DIR/setup-database.sh"
            if "$SCRIPT_DIR/setup-database.sh"; then
                print_success "Database setup completed"
            else
                print_warning "Database setup failed (this is okay if PostgreSQL isn't running)"
            fi
        else
            print_warning "Database setup script not found"
        fi
        echo ""
    fi

    # Claude Code setup
    if [ "$SKIP_CLAUDE" = false ]; then
        print_header "🤖 Setting up Claude Code..."
        if [ -f "$SCRIPT_DIR/setup-claude-code.sh" ]; then
            chmod +x "$SCRIPT_DIR/setup-claude-code.sh"
            if "$SCRIPT_DIR/setup-claude-code.sh"; then
                print_success "Claude Code setup completed"
            else
                print_warning "Claude Code setup failed (this is okay if Claude Code isn't installed)"
            fi
        else
            print_warning "Claude Code setup script not found"
        fi
        echo ""
    fi

    # Final status
    print_header "🎉 Setup Complete!"
    echo ""
    print_status "Your TaskFlow development environment is ready!"
    echo ""
    print_header "🚀 Quick Start:"
    echo "1. Start the database:    docker-compose -f docker-compose.dev.yml up -d postgres"
    echo "2. Start the backend:     cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "3. Start the frontend:    cd frontend && npm run dev"
    echo ""
    print_header "🔧 Available Commands:"
    echo "Frontend:"
    echo "  cd frontend && npm run dev      - Start development server"
    echo "  cd frontend && npm run build    - Build for production"
    echo "  cd frontend && npm run test     - Run tests"
    echo ""
    echo "Backend:"
    echo "  cd backend && source venv/bin/activate  - Activate Python environment"
    echo "  cd backend && uvicorn main:app --reload - Start FastAPI server"
    echo "  cd backend && pytest                    - Run tests"
    echo ""
    echo "Database:"
    echo "  docker-compose -f docker-compose.dev.yml up -d    - Start all services"
    echo "  docker-compose -f docker-compose.dev.yml down     - Stop all services"
    echo ""
    print_status "Happy coding! 🎯"
}

# Help function
show_help() {
    echo "TaskFlow Development Environment Setup"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-frontend     Skip frontend setup"
    echo "  --skip-backend      Skip backend setup"
    echo "  --skip-database     Skip database setup"
    echo "  --skip-claude       Skip Claude Code setup"
    echo "  --verbose, -v       Run without confirmation prompts"
    echo "  --help, -h          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Full setup with confirmation"
    echo "  $0 --verbose                # Full setup without confirmation"
    echo "  $0 --skip-database          # Setup without database"
    echo "  $0 --skip-frontend --skip-backend  # Only database and Claude Code"
}

# Run main function
main "$@"