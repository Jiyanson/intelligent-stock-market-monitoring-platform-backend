#!/bin/bash
#
# Docker Cleanup Script for DevSecOps Pipeline
# Removes conflicting containers, cleans up resources, and frees ports
#
# Usage: ./cleanup_docker.sh

set -e

echo "=================================================="
echo "🧹 Docker Cleanup Script"
echo "=================================================="

# Stop all services managed by docker-compose
echo ""
echo "[1/7] Stopping docker-compose services..."
docker compose down --remove-orphans --volumes || {
    echo "⚠️  docker-compose down failed, continuing..."
}

# Force remove named containers
echo ""
echo "[2/7] Removing named containers..."
NAMED_CONTAINERS="postgres_db redis_cache pgadmin"
for container in $NAMED_CONTAINERS; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "  🗑️  Removing container: $container"
        docker rm -f "$container" 2>/dev/null || true
    else
        echo "  ✅ Container not found: $container"
    fi
done

# Remove any containers from this project
echo ""
echo "[3/7] Removing project containers..."
docker ps -a --filter "name=devsecops2" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || {
    echo "  ℹ️  No project containers to remove"
}
docker compose ps -aq 2>/dev/null | xargs -r docker rm -f 2>/dev/null || {
    echo "  ℹ️  No additional containers to remove"
}

# Clean up networks
echo ""
echo "[4/7] Cleaning up networks..."
# Remove project-specific network
docker network ls --filter name=devsecops --format '{{.Name}}' | xargs -r docker network rm 2>/dev/null || true
# Prune unused networks
docker network prune -f || true

# Check and free up ports
echo ""
echo "[5/7] Checking critical ports..."
PORTS="8000 5432 6379 5050"
for port in $PORTS; do
    if lsof -i :${port} >/dev/null 2>&1; then
        echo "  ⚠️  Port ${port} is in use:"
        lsof -i :${port} || true
        echo "  🔧 Attempting to free port ${port}..."
        lsof -ti :${port} | xargs -r kill -9 2>/dev/null || true
        sleep 1
        if lsof -i :${port} >/dev/null 2>&1; then
            echo "  ❌ Port ${port} could not be freed (may require manual intervention)"
        else
            echo "  ✅ Port ${port} freed"
        fi
    else
        echo "  ✅ Port ${port} is free"
    fi
done

# Clean up volumes (OPTIONAL - uncomment if needed)
echo ""
echo "[6/7] Cleaning up volumes..."
# Uncomment the next line to remove volumes (THIS WILL DELETE DATABASE DATA!)
# docker volume prune -f || true
echo "  ℹ️  Volume cleanup skipped (data preserved)"
echo "  💡 To remove volumes: docker volume prune -f"

# Clean up dangling images
echo ""
echo "[7/7] Cleaning up dangling images..."
docker image prune -f || true

echo ""
echo "=================================================="
echo "✅ Cleanup completed!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run: docker compose up -d"
echo "  2. Check status: docker compose ps"
echo ""
echo "To see what's running:"
echo "  docker ps -a"
echo ""
