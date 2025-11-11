# AI Processor Image Setup

The AI Processor image contains ML/AI packages (transformers, torch, DeepSeek R1) used for security policy generation. This image should be built **once** and pushed to Docker Hub, then the Jenkins pipeline will pull it automatically.

## Initial Setup (One-time only)

### 1. Build the AI Processor Image

```bash
docker build -f Dockerfile.ai-processor -t michoc/ai-security-processor:latest .
```

**Note:** This will take 5-10 minutes as it downloads large ML packages (~2GB+).

### 2. Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push the image
docker push michoc/ai-security-processor:latest
```

### 3. Done!

The Jenkins pipeline will now automatically pull this pre-built image during every run. No rebuilding needed!

## When to Rebuild

You only need to rebuild the AI Processor image when:
- You want to update ML package versions (transformers, torch, etc.)
- You add new Python dependencies to `Dockerfile.ai-processor`
- You want to use a different base Python version

## Update Instructions

```bash
# 1. Edit Dockerfile.ai-processor (update package versions)
# 2. Rebuild
docker build -f Dockerfile.ai-processor -t michoc/ai-security-processor:latest .

# 3. Push updated image
docker push michoc/ai-security-processor:latest

# 4. Next pipeline run will use the updated image automatically
```

## Image Size

- Base Python image: ~150MB
- With ML packages: ~2-3GB
- This is why we cache it!

## Troubleshooting

**Pipeline fails with "AI Processor image not found":**
```bash
# The image hasn't been pushed to Docker Hub yet
# Run the initial setup commands above
```

**Want to force pipeline to use latest version:**
```bash
# Delete local cache
docker rmi michoc/ai-security-processor:latest

# Pipeline will pull fresh image from registry
```
