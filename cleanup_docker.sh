#!/bin/bash
#
# Docker Cleanup Script for DevSecOps Pipeline
# Removes conflicting containers and cleans up resources
#
# Usage: ./cleanup_docker.sh

set -e

echo "=================================================="
echo "🧹 Docker Cleanup Script"
echo "=================================================="

# Stop all services managed by docker-compose
echo ""
echo "[1/6] Stopping docker-compose services..."
docker compose down --remove-orphans || {
    echo "⚠️  docker-compose down failed, continuing..."
}

# Force remove named containers
echo ""
echo "[2/6] Removing named containers..."
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
echo "[3/6] Removing project containers..."
docker compose ps -aq | xargs -r docker rm -f 2>/dev/null || {
    echo "  ℹ️  No additional containers to remove"
}

# Clean up networks
echo ""
echo "[4/6] Cleaning up networks..."
# Remove project-specific network
docker network ls --filter name=devsecops --format '{{.Name}}' | xargs -r docker network rm 2>/dev/null || true
# Prune unused networks
docker network prune -f || true

# Clean up volumes (OPTIONAL - uncomment if needed)
echo ""
echo "[5/6] Cleaning up volumes..."
# Uncomment the next line to remove volumes (THIS WILL DELETE DATABASE DATA!)
# docker volume prune -f || true
echo "  ℹ️  Volume cleanup skipped (data preserved)"
echo "  💡 To remove volumes: docker volume prune -f"

# Clean up dangling images
echo ""
echo "[6/6] Cleaning up dangling images..."
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
