# Docker BBC iPlayer Fix

## Problem

When running AniWorld Downloader in Docker, BBC iPlayer searches fail with:
```
ERROR - ../usr/local/lib/python3.13/site-packages/aniworld/search.py:832:query_bbc_iplayer 
- Error searching BBC iPlayer: get_iplayer not found. Please install get_iplayer or provide its path.
```

This occurs because the Docker container doesn't have `get_iplayer` installed or available.

## Solution

The repository has been updated with the following changes:

### 1. **Updated Dockerfile**
   - Added Perl and required Perl dependencies to the apt-get install
   - Added copy of `get_iplayer` executable from `get_iplayer-master/` directory
   - Installs `get_iplayer` to `/usr/local/bin/` in the container

### 2. **Updated docker-compose.yaml**
   - Changed default to use local build (`build: .`) instead of pre-built image
   - This ensures the Dockerfile changes are applied

### 3. **Updated get_iplayer_api.py**
   - Removed hardcoded local path references
   - Now properly detects `get_iplayer` via PATH

## How to Fix Your Setup

### Option 1: Rebuild from Updated Code (Recommended)

```bash
# Navigate to the project directory
cd /path/to/AniWorld-Downloader

# Ensure get_iplayer-master directory exists
ls -la get_iplayer-master/get_iplayer

# Pull latest changes
git pull

# Rebuild the Docker image
docker-compose build --no-cache

# Start the container
docker-compose up -d

# Verify logs
docker-compose logs -f
```

### Option 2: Manual Docker Build

```bash
# Build with get_iplayer support
docker build -t aniworld-downloader:latest .

# Run the container
docker run -d \
  -p 8080:8080 \
  -v ./Downloads:/app/Downloads \
  -v aniworld-data:/home/aniworld/.aniworld \
  --name aniworld-downloader \
  aniworld-downloader:latest
```

### Option 3: Use Pre-built Image (Wait for Release)

The pre-built image on GitHub Container Registry will be updated in the next release. Once available:

```bash
# Update docker-compose.yaml to use pre-built image
# Change: build: .
# To:     image: ghcr.io/phoenixthrush/aniworld-downloader:latest

docker-compose pull
docker-compose up -d
```

## Verification

After rebuilding, verify the fix:

```bash
# Check logs for successful initialization
docker-compose logs -f

# The BBC iPlayer button should now work in the web UI
# Try searching for a BBC programme
```

Look for successful search results instead of the error message.

## What Was Changed

### Dockerfile Changes

**Added Dependencies:**
```dockerfile
perl \
libwww-perl \
libxml-libxml-perl \
libjson-perl \
libmojolicious-perl \
```

**Added get_iplayer Installation:**
```dockerfile
COPY get_iplayer-master/get_iplayer /usr/local/bin/get_iplayer
RUN chmod +x /usr/local/bin/get_iplayer
```

### docker-compose.yaml Changes

**Changed from:**
```yaml
image: ghcr.io/phoenixthrush/aniworld-downloader:latest
```

**To:**
```yaml
build: .
```

### Code Changes

**Removed hardcoded path** from `src/aniworld/models/bbc_iplayer/get_iplayer_api.py`:
```python
# REMOVED:
Path("/Users/hannesnemitz/Documents/GitHub/AniWorld-Downloader/get_iplayer-master/get_iplayer"),

# KEPT:
Path("/usr/bin/get_iplayer"),
Path("/usr/local/bin/get_iplayer"),
Path("/opt/homebrew/bin/get_iplayer"),
# Plus PATH lookup via `which get_iplayer`
```

## Files Modified

1. `Dockerfile` - Added get_iplayer dependencies and installation
2. `docker-compose.yaml` - Changed to use local build
3. `src/aniworld/models/bbc_iplayer/get_iplayer_api.py` - Removed hardcoded path

## Troubleshooting

### If the rebuild fails:

1. **Check if get_iplayer-master exists:**
   ```bash
   ls -la get_iplayer-master/get_iplayer
   ```

2. **Verify Dockerfile exists:**
   ```bash
   ls -la Dockerfile
   ```

3. **Clean and rebuild:**
   ```bash
   docker-compose down
   docker system prune
   docker-compose build --no-cache
   ```

4. **Check Docker build logs:**
   ```bash
   docker-compose build --no-cache 2>&1 | tail -100
   ```

### If BBC iPlayer still doesn't work:

1. **Check container logs:**
   ```bash
   docker-compose logs -f aniworld
   ```

2. **Verify get_iplayer is in container:**
   ```bash
   docker-compose exec aniworld which get_iplayer
   ```

3. **Test get_iplayer in container:**
   ```bash
   docker-compose exec aniworld get_iplayer --help
   ```

## Additional Notes

- The `get_iplayer-master` directory must be in the repository root
- The `get_iplayer` executable must have execute permissions (should be `755`)
- Perl dependencies are required for get_iplayer to function
- BBC iPlayer only indexes programmes from the last 30 days
- Only available from UK IP addresses (BBC licensing requirement)

## Need Help?

If you continue to experience issues:

1. Check that the Docker image was successfully built:
   ```bash
   docker images | grep aniworld
   ```

2. Verify get_iplayer is available in the container:
   ```bash
   docker-compose run --rm aniworld get_iplayer --version
   ```

3. Test BBC iPlayer search manually:
   ```bash
   docker-compose exec aniworld get_iplayer "test search"
   ```
