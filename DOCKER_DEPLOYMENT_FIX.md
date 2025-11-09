# Docker Deployment Fix - Container Name Conflicts

## Problem

Jenkins pipeline deployment was failing with container name conflicts:

```
Error response from daemon: Conflict. The container name "/redis_cache" is already in use
Error response from daemon: Conflict. The container name "/postgres_db" is already in use
```

**Additional Warning:**
```
the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
```

## Root Cause

1. **Named Containers Not Cleaned Up**
   - Docker Compose uses explicit container names (`postgres_db`, `redis_cache`, `pgadmin`)
   - `docker compose down` wasn't removing these containers completely
   - Containers from previous runs were still present

2. **Orphaned Networks**
   - Docker networks from previous deployments weren't being cleaned up
   - Network conflicts prevented new container creation

3. **Obsolete docker-compose.yml Syntax**
   - `version: '3.9'` field is now obsolete in Docker Compose v2

## Solution Implemented

### 1. Updated docker-compose.yml

**Removed:** Obsolete `version` field
```yaml
# BEFORE:
version: '3.9'

services:
  ...

# AFTER:
services:
  ...
```

### 2. Enhanced Jenkinsfile Deployment Stage

**Added comprehensive cleanup:**
```bash
# Clean up existing deployment
docker compose down --remove-orphans || true

# Force remove named containers if they still exist
docker rm -f postgres_db redis_cache pgadmin 2>/dev/null || true

# Clean up any networks from previous runs
docker network prune -f || true

# Pull latest image
docker pull ${IMAGE_NAME}:latest

# Start services
docker compose up -d

# Wait and verify
sleep 10
docker compose ps
```

**Key Improvements:**
- `--remove-orphans` flag removes containers not defined in current compose file
- Explicit container removal with `docker rm -f` for named containers
- Network cleanup with `docker network prune -f`
- Service verification after deployment
- Better logging and error messages

### 3. Created cleanup_docker.sh Script

**Manual cleanup utility** for emergency situations:
```bash
./cleanup_docker.sh
```

**What it does:**
1. Stops all docker-compose services
2. Force removes named containers (`postgres_db`, `redis_cache`, `pgadmin`)
3. Removes project containers
4. Cleans up networks
5. Prunes dangling images
6. (Optional) Prunes volumes

## Usage

### Automatic (Jenkins Pipeline)

The deployment stage now automatically handles cleanup:
```groovy
stage('Deploy') {
    // Automatically cleans up and redeploys
}
```

### Manual Cleanup

If you encounter container conflicts manually:

**Option 1: Use the cleanup script**
```bash
./cleanup_docker.sh
docker compose up -d
```

**Option 2: Manual commands**
```bash
# Stop everything
docker compose down --remove-orphans

# Force remove named containers
docker rm -f postgres_db redis_cache pgadmin

# Clean networks
docker network prune -f

# Restart
docker compose up -d
```

### Check Container Status

```bash
# See all containers
docker ps -a

# See only project containers
docker compose ps

# See logs if services aren't starting
docker compose logs --tail=50
```

## Prevention

### Best Practices

1. **Always use `--remove-orphans`**
   ```bash
   docker compose down --remove-orphans
   ```

2. **Clean up before deployment**
   ```bash
   docker compose down --remove-orphans
   docker rm -f $(docker ps -aq --filter name=postgres_db) 2>/dev/null || true
   ```

3. **Prune regularly**
   ```bash
   docker system prune -f
   docker network prune -f
   ```

4. **Avoid hardcoded container names** (if possible)
   - Let Docker Compose generate names automatically
   - Or use project-specific prefixes

### Monitoring

Add to deployment scripts:
```bash
# Before deployment
echo "Current containers:"
docker ps -a --filter name=postgres_db --filter name=redis_cache

# After deployment
echo "Deployment status:"
docker compose ps
```

## Troubleshooting

### Issue: Containers still won't start

**Solution:**
```bash
# Nuclear option - stop ALL containers
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker network prune -f
docker volume prune -f  # WARNING: Deletes data!

# Then redeploy
docker compose up -d
```

### Issue: Network conflicts

**Solution:**
```bash
# List all networks
docker network ls

# Remove specific network
docker network rm devsecops2_default

# Or prune all unused networks
docker network prune -f
```

### Issue: Port already in use

**Solution:**
```bash
# Find what's using the port (e.g., 5432 for PostgreSQL)
sudo lsof -i :5432
# or
sudo netstat -tulpn | grep 5432

# Kill the process or remove the container
docker stop <container_id>
```

### Issue: Volume conflicts

**Solution:**
```bash
# List volumes
docker volume ls

# Remove specific volume
docker volume rm devsecops2_pgdata

# Or prune unused volumes (WARNING: Deletes data!)
docker volume prune -f
```

## Files Modified

1. **docker-compose.yml**
   - Removed obsolete `version: '3.9'` field

2. **jenkinsfile**
   - Enhanced `Deploy` stage with comprehensive cleanup
   - Added orphan removal, network cleanup, and verification

3. **cleanup_docker.sh** (NEW)
   - Manual cleanup utility
   - Safe cleanup with data preservation options

## Testing

### Verify the fix works:

1. **Simulate the issue:**
   ```bash
   # Create conflicting containers
   docker run -d --name postgres_db postgres:15
   docker run -d --name redis_cache redis:7
   ```

2. **Run deployment:**
   ```bash
   # Should now clean up and deploy successfully
   cd /path/to/project
   docker compose down --remove-orphans
   docker rm -f postgres_db redis_cache pgadmin
   docker compose up -d
   ```

3. **Verify:**
   ```bash
   docker compose ps
   # All services should be "Up"
   ```

### Expected Output

**Before fix:**
```
Error response from daemon: Conflict. The container name "/redis_cache" is already in use
```

**After fix:**
```
🧹 Cleaning up existing containers...
Removing postgres_db ... done
Removing redis_cache ... done

📥 Pulling latest image...
latest: Pulling from michoc/stock-market-platform

🚀 Starting services...
Creating postgres_db ... done
Creating redis_cache ... done

✅ Deployment completed successfully
```

## Impact

✅ **No more container name conflicts**
✅ **Clean deployment every time**
✅ **Proper cleanup of orphaned resources**
✅ **Better error handling and logging**
✅ **Manual cleanup option available**
✅ **Removed obsolete Docker Compose syntax**

## Additional Notes

### About Named Containers

The docker-compose.yml uses explicit container names:
```yaml
db:
  container_name: postgres_db  # Explicit name

redis:
  container_name: redis_cache  # Explicit name
```

**Pros:**
- Predictable container names
- Easier to reference in scripts
- Consistent across deployments

**Cons:**
- Can cause conflicts if not cleaned up properly
- Can't run multiple instances of the same compose file

**Alternative:** Remove container_name and let Docker Compose generate names:
```yaml
db:
  # No container_name - Docker generates: projectname_db_1
```

### Jenkins-Specific Considerations

On Jenkins, the workspace might be in:
```
/var/lib/jenkins/workspace/devsecops2/
```

The cleanup script will work regardless of the working directory because it uses Docker commands that are workspace-agnostic.

## Summary

**Problem:** Container name conflicts preventing deployment
**Cause:** Incomplete cleanup of named containers and networks
**Solution:** Enhanced cleanup in deployment stage + manual cleanup script
**Result:** Reliable, conflict-free deployments

✅ **Fix is production-ready!**
