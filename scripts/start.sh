#!/bin/bash
set -e

echo "🚀 Starting PDF Parser Service..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker compose build --no-cache
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
timeout 60 bash -c 'until docker compose ps | grep -q "healthy"; do sleep 2; done'

# Check service status
echo "📋 Service Status:"
docker compose ps

echo ""
echo "✅ Services are ready!"
echo "🌐 API available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/api/v1/health"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down" 