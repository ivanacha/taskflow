#!/bin/bash
echo "🔄 Resetting TaskFlow development environment..."
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
echo "✅ Development environment reset!"
