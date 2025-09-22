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
