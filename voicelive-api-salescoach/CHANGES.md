# Deployment Changes and Fixes

## Date: November 5, 2025

## Overview
Successfully deployed the VoiceLive API Sales Coach application to Azure Container Apps from a Windows ARM64 development environment.

**Deployed Endpoint:** https://voicelab.blackcoast-8ce9895b.eastus2.azurecontainerapps.io/

---

## Challenges Faced

### 1. Platform Architecture Mismatch (ARM64 vs AMD64)

**Problem:**
- Development environment: Windows ARM64
- Target deployment platform: Azure Container Apps (AMD64/x86_64)
- Docker build attempts resulted in "exec /bin/sh: exec format error"

**Root Cause:**
Docker was attempting to build AMD64 images on an ARM64 host without proper emulation support, causing binary incompatibility.

**Initial Error:**
```
exec /bin/sh: exec format error
ERROR: process "/bin/sh -c apt-get update && apt-get install..." did not complete successfully: exit code: 255
```

### 2. Missing Multi-Platform Build Support

**Problem:**
The default Docker builder only supported `linux/arm64` platform.

**Evidence:**
```bash
$ docker buildx ls
NAME/NODE         DRIVER/ENDPOINT   STATUS   PLATFORMS
desktop-linux*    docker                     linux/arm64
```

**Solution:**
Created a new buildx builder with multi-platform support and installed QEMU emulators:

```bash
docker buildx create --name multiplatform --driver docker-container --bootstrap --use
docker run --privileged --rm tonistiigi/binfmt --install all
```

This enabled support for multiple platforms including `linux/amd64`, `linux/arm64`, and others.

### 3. Emulation Performance and Stability Issues

**Problem:**
Even with QEMU emulation installed, building complex Node.js applications (using esbuild/Vite) under ARM64→AMD64 emulation caused fatal crashes.

**Error Encountered:**
```
runtime: lfstack.push invalid packing
fatal error: lfstack.push
```

**Root Cause:**
Go-based build tools (esbuild) running under QEMU emulation experienced memory corruption and stability issues due to the complexity of cross-architecture emulation.

---

## Solutions Implemented

### Solution 1: Enable Azure Container Registry Remote Build

Modified `azure.yaml` to use remote builds in Azure Container Registry instead of local Docker builds:

**File:** `azure.yaml`
```yaml
services:
  voicelab:
    project: backend
    host: containerapp
    language: python
    docker:
      path: Dockerfile
      context: ../
      remoteBuild: true  # ← Added this
```

**Benefits:**
- Builds happen on native AMD64 hardware in Azure
- No emulation overhead
- Faster build times
- More reliable builds

### Solution 2: Clean Up Dockerfile Platform Directives

Removed explicit `--platform` flags from Dockerfile since Azure Container Registry builds natively on AMD64:

**File:** `backend/Dockerfile`

**Before:**
```dockerfile
FROM --platform=linux/amd64 node:20-alpine AS frontend-builder
...
FROM --platform=linux/amd64 python:3.11-slim-bullseye
```

**After:**
```dockerfile
FROM node:20-alpine AS frontend-builder
...
FROM python:3.11-slim-bullseye
```

This also resolved Docker build warnings about constant platform values.

---

## Deployment Results

### Successfully Provisioned Resources

1. **Resource Group:** `rg-nbk-avatar`
2. **Container Registry:** `cr6ng26fguwmnci`
3. **Container Apps Environment:** `cae-6ng26fguwmnci`
4. **Container App:** `voicelab`
5. **Azure AI Services:**
   - Speech Service: `speech-voicelab-6ng26fguwmnci`
   - AI Foundry: `aifoundry-voicelab-6ng26fguwmnci`
   - Model Deployments: `gpt-4o`, `text-embedding-ada-002`
6. **Monitoring:**
   - Application Insights: `appi-6ng26fguwmnci`
   - Log Analytics: `log-6ng26fguwmnci`
7. **Portal Dashboard:** `dash-6ng26fguwmnci`

### Deployment Timeline
- Total deployment time: **6 minutes 42 seconds**
- Resource provisioning completed successfully
- Application deployed and running

---

## Key Learnings

1. **Cross-Platform Development:** When developing on ARM64 (Apple Silicon, Windows ARM) for AMD64 cloud deployments, use cloud-native build services rather than local emulation.

2. **Azure Developer CLI Best Practice:** The `remoteBuild: true` option in `azure.yaml` is essential for ARM64 development environments deploying to Azure.

3. **Docker Multi-Platform Builds:** While QEMU emulation works for simple applications, complex build tools may require native architecture builds.

4. **Development Workflow:** For ARM64 developers:
   - Use `remoteBuild: true` for Azure deployments
   - Consider GitHub Actions or Azure Pipelines for CI/CD
   - Avoid local Docker builds for complex multi-stage builds

---

## Files Modified

1. `azure.yaml` - Added `remoteBuild: true` configuration
2. `backend/Dockerfile` - Removed explicit platform directives
3. `CHANGES.md` - This documentation

---

## Verification

Application successfully accessible at:
- **URL:** https://voicelab.blackcoast-8ce9895b.eastus2.azurecontainerapps.io/
- **Status:** Running
- **Health Check:** Passing
