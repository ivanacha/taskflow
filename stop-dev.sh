#!/bin/bash
echo "🛑 Stopping TaskFlow development environment..."
docker-compose -f docker-compose.dev.yml down
echo "✅ Development environment stopped!"
