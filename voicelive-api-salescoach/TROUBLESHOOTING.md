# Troubleshooting Guide

This guide addresses common issues encountered during deployment and provides quick solutions.

## Issue: Avatar Not Loading After Successful Deployment

### Symptoms
- `azd up` completes successfully
- Container App is running and accessible
- Website loads but Avatar doesn't appear
- Application logs show: "OpenAI not configured" or "not configured - falling back to instruction-based approach"

### Root Cause
Azure Container Apps doesn't always create a new revision when only Bicep-defined environment variables change. This means the container is running without the required configuration.

### Quick Diagnosis

1. **Check environment variables count:**
   ```bash
   az containerapp show --name voicelab --resource-group <your-rg> \
     --query "properties.template.containers[0].env[].name" -o tsv | wc -l
   ```
   - **Expected:** 27 environment variables
   - **Problem:** Only 3 variables (APPLICATIONINSIGHTS_CONNECTION_STRING, AZURE_CLIENT_ID, PORT)

2. **Check application logs:**
   ```bash
   az containerapp logs show --name voicelab --resource-group <your-rg> --tail 20
   ```
   - **Problem indicators:**
     - "OpenAI not configured for scenario generation"
     - "OpenAI endpoint or API key not configured"
     - "not configured - falling back to instruction-based approach"

### Solution: Manual Container App Update

When Bicep deployment doesn't apply environment variables, you must manually update the Container App.

#### PowerShell Commands

```powershell
# Set your variables
$RESOURCE_GROUP = "rg-nbk-avatar"
$CONTAINER_APP_NAME = "voicelab"
$AI_FOUNDRY_NAME = "aifoundry-voicelab-6ng26fguwmnci"
$SPEECH_SERVICE_NAME = "speech-voicelab-6ng26fguwmnci"
$BING_RESOURCE_NAME = "r-bing-nbk"
$AGENT_ID = "asst_wgsM81Hm1FuLOJemAeEfrYQr"

# Step 1: Get API keys
$speechKey = (az cognitiveservices account keys list `
  --name $SPEECH_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query key1 -o tsv)

$aiKey = (az cognitiveservices account keys list `
  --name $AI_FOUNDRY_NAME `
  --resource-group $RESOURCE_GROUP `
  --query key1 -o tsv)

$bingKey = (az cognitiveservices account keys list `
  --name $BING_RESOURCE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query key1 -o tsv)

# Step 2: Set secrets
az containerapp secret set `
  --name $CONTAINER_APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --secrets `
    "ai-foundry-api-key=$aiKey" `
    "speech-api-key=$speechKey" `
    "bing-grounding-api-key=$bingKey"

# Step 3: Get configuration values
$aiEndpoint = (az cognitiveservices account show `
  --name $AI_FOUNDRY_NAME `
  --resource-group $RESOURCE_GROUP `
  --query properties.endpoint -o tsv)

$speechRegion = (az cognitiveservices account show `
  --name $SPEECH_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query location -o tsv)

$subscriptionId = (az account show --query id -o tsv)

# Step 4: Update Container App with all environment variables
az containerapp update `
  --name $CONTAINER_APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars `
    "AZURE_OPENAI_ENDPOINT=$aiEndpoint" `
    "AZURE_OPENAI_API_KEY=secretref:ai-foundry-api-key" `
    "PROJECT_ENDPOINT=${aiEndpoint}api/projects/aifoundry-voicelab-6ng2-project" `
    "MODEL_DEPLOYMENT_NAME=gpt-4o" `
    "AZURE_SPEECH_KEY=secretref:speech-api-key" `
    "AZURE_SPEECH_REGION=$speechRegion" `
    "AZURE_AI_RESOURCE_NAME=$AI_FOUNDRY_NAME" `
    "AZURE_AI_REGION=$speechRegion" `
    "AZURE_AI_PROJECT_NAME=aifoundry-voicelab-6ng2-project" `
    "USE_AZURE_AI_AGENTS=true" `
    "AGENT_ID=$AGENT_ID" `
    "BING_GROUNDING_RESOURCE_NAME=$BING_RESOURCE_NAME" `
    "BING_GROUNDING_RESOURCE_KEY=secretref:bing-grounding-api-key" `
    "BING_GROUNDING_CONFIG_ID=" `
    "AZURE_VOICE_NAME=en-US-AndrewMultilingualNeural" `
    "AZURE_SPEECH_LANGUAGE=ar-SA,en-US" `
    "AZURE_AVATAR_CHARACTER=jeff" `
    "AZURE_AVATAR_STYLE=business" `
    "AZURE_INPUT_TRANSCRIPTION_MODEL=azure-speech" `
    "AZURE_INPUT_TRANSCRIPTION_LANGUAGE=ar-SA,en-US" `
    "AZURE_INPUT_NOISE_REDUCTION_TYPE=azure_deep_noise_suppression" `
    "AZURE_VOICE_TYPE=azure-standard" `
    "SUBSCRIPTION_ID=$subscriptionId" `
    "RESOURCE_GROUP_NAME=$RESOURCE_GROUP"
```

#### Bash Commands

```bash
# Set your variables
RESOURCE_GROUP="rg-nbk-avatar"
CONTAINER_APP_NAME="voicelab"
AI_FOUNDRY_NAME="aifoundry-voicelab-6ng26fguwmnci"
SPEECH_SERVICE_NAME="speech-voicelab-6ng26fguwmnci"
BING_RESOURCE_NAME="r-bing-nbk"
AGENT_ID="asst_wgsM81Hm1FuLOJemAeEfrYQr"

# Step 1: Get API keys
SPEECH_KEY=$(az cognitiveservices account keys list \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

AI_KEY=$(az cognitiveservices account keys list \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

BING_KEY=$(az cognitiveservices account keys list \
  --name $BING_RESOURCE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

# Step 2: Set secrets
az containerapp secret set \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    "ai-foundry-api-key=$AI_KEY" \
    "speech-api-key=$SPEECH_KEY" \
    "bing-grounding-api-key=$BING_KEY"

# Step 3: Get configuration values
AI_ENDPOINT=$(az cognitiveservices account show \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

SPEECH_REGION=$(az cognitiveservices account show \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query location -o tsv)

SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Step 4: Update Container App with all environment variables
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    "AZURE_OPENAI_ENDPOINT=$AI_ENDPOINT" \
    "AZURE_OPENAI_API_KEY=secretref:ai-foundry-api-key" \
    "PROJECT_ENDPOINT=${AI_ENDPOINT}api/projects/aifoundry-voicelab-6ng2-project" \
    "MODEL_DEPLOYMENT_NAME=gpt-4o" \
    "AZURE_SPEECH_KEY=secretref:speech-api-key" \
    "AZURE_SPEECH_REGION=$SPEECH_REGION" \
    "AZURE_AI_RESOURCE_NAME=$AI_FOUNDRY_NAME" \
    "AZURE_AI_REGION=$SPEECH_REGION" \
    "AZURE_AI_PROJECT_NAME=aifoundry-voicelab-6ng2-project" \
    "USE_AZURE_AI_AGENTS=true" \
    "AGENT_ID=$AGENT_ID" \
    "BING_GROUNDING_RESOURCE_NAME=$BING_RESOURCE_NAME" \
    "BING_GROUNDING_RESOURCE_KEY=secretref:bing-grounding-api-key" \
    "BING_GROUNDING_CONFIG_ID=" \
    "AZURE_VOICE_NAME=en-US-AndrewMultilingualNeural" \
    "AZURE_SPEECH_LANGUAGE=ar-SA,en-US" \
    "AZURE_AVATAR_CHARACTER=jeff" \
    "AZURE_AVATAR_STYLE=business" \
    "AZURE_INPUT_TRANSCRIPTION_MODEL=azure-speech" \
    "AZURE_INPUT_TRANSCRIPTION_LANGUAGE=ar-SA,en-US" \
    "AZURE_INPUT_NOISE_REDUCTION_TYPE=azure_deep_noise_suppression" \
    "AZURE_VOICE_TYPE=azure-standard" \
    "SUBSCRIPTION_ID=$SUBSCRIPTION_ID" \
    "RESOURCE_GROUP_NAME=$RESOURCE_GROUP"
```

### Verification

After running the update command:

1. **Check new revision created:**
   ```bash
   az containerapp revision list --name voicelab --resource-group $RESOURCE_GROUP -o table
   ```
   You should see a new revision (e.g., `voicelab--0000004`)

2. **Verify environment variables:**
   ```bash
   az containerapp show --name voicelab --resource-group $RESOURCE_GROUP \
     --query "properties.template.containers[0].env[].name" -o tsv
   ```
   Should show 27 variables

3. **Check Avatar configuration:**
   ```bash
   az containerapp show --name voicelab --resource-group $RESOURCE_GROUP \
     --query "properties.template.containers[0].env[?name=='AZURE_VOICE_NAME' || name=='AZURE_AVATAR_CHARACTER'].{Name:name,Value:value}" -o table
   ```
   Should show:
   - AZURE_VOICE_NAME: en-US-AndrewMultilingualNeural
   - AZURE_AVATAR_CHARACTER: jeff

4. **Check application logs:**
   ```bash
   az containerapp logs show --name voicelab --resource-group $RESOURCE_GROUP --tail 20
   ```
   Should show:
   - "pre-configured Azure AI Foundry agent: asst_xxxxx"
   - "initialized with Azure AI Agent Service support"
   - "initialized with endpoint: https://..."

---

## Issue: Docker Build "Directory Name is Invalid"

### Symptoms
```
ERROR: invalid argument "backend" for "-t" flag: invalid reference format
```

### Root Cause
Incorrect `project` path in `azure.yaml`

### Solution
Edit `azure.yaml` in root directory:

```yaml
services:
  voicelab:
    project: voicelive-api-salescoach/backend  # NOT just "backend"
    docker:
      context: ../
```

---

## Issue: Slow Remote Build (Large Context)

### Symptoms
- Build takes 10+ minutes
- Upload shows 289 MB, 33,528 files
- Message: "Uploading build context..."

### Root Cause
`node_modules` and `venv` included in Docker build context

### Solution
Update `voicelive-api-salescoach/.dockerignore`:

```
**/node_modules/
frontend/node_modules/
backend/venv/
backend/env/
backend/.venv/
backend/__pycache__/
**/__pycache__/
**/*.pyc
.git/
```

**Important:** Use `**/node_modules/` pattern, not just `node_modules/`

---

## Issue: "exec format error" (Platform Mismatch)

### Symptoms
Container fails to start with:
```
exec /usr/local/bin/python: exec format error
```

### Root Cause
Container built for wrong architecture (ARM64 instead of AMD64)

### Solution
**Do NOT add `--platform` flags to Dockerfile.** Azure Container Registry automatically builds for linux/amd64 when using `remoteBuild: true`.

If you previously added platform flags, remove them:

```dockerfile
# WRONG - Remove these:
FROM --platform=linux/amd64 node:20-alpine AS frontend-builder
FROM --platform=linux/amd64 python:3.11-slim-bullseye

# CORRECT - No platform flags:
FROM node:20-alpine AS frontend-builder
FROM python:3.11-slim-bullseye
```

---

## Issue: SSL Certificate Errors During npm Install

### Symptoms
```
Error: unable to get local issuer certificate
```

### Root Cause
Corporate proxy or firewall blocking npm registry

### Solution
Add to Dockerfile frontend-builder stage:

```dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app
RUN npm config set strict-ssl false
```

---

## Issue: Agent Not Responding

### Symptoms
- Avatar appears but doesn't respond
- Logs show: "Agent run failed" or "Agent not found"

### Diagnosis
Check if Agent ID is correct:

```bash
az containerapp show --name voicelab --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env[?name=='AGENT_ID'].value" -o tsv
```

### Solution
1. Verify Agent exists in Azure AI Foundry Portal
2. Copy correct Agent ID (format: `asst_xxxxxxxxxxxxxxxxxxxxx`)
3. Update environment variable:

```bash
az containerapp update --name voicelab --resource-group $RESOURCE_GROUP \
  --set-env-vars "AGENT_ID=asst_YourCorrectAgentId"
```

---

## Issue: Wrong Voice or Avatar Character

### Symptoms
Avatar appears but with wrong voice or character

### Solution
Update Avatar configuration:

```bash
az containerapp update --name voicelab --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    "AZURE_VOICE_NAME=en-US-AndrewMultilingualNeural" \
    "AZURE_AVATAR_CHARACTER=jeff" \
    "AZURE_AVATAR_STYLE=business" \
    "AZURE_SPEECH_LANGUAGE=ar-SA,en-US"
```

Available voices: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts

---

## Quick Reference: Important Commands

### Get Container App URL
```bash
az containerapp show --name voicelab --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

### Stream Logs
```bash
az containerapp logs show --name voicelab --resource-group $RESOURCE_GROUP --follow
```

### List Environment Variables
```bash
az containerapp show --name voicelab --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env[].{Name:name,Value:value,Secret:secretRef}" -o table
```

### Force New Revision
```bash
az containerapp update --name voicelab --resource-group $RESOURCE_GROUP \
  --revision-suffix "manual-$(date +%s)"
```

### Restart Container App
```bash
az containerapp revision restart --name voicelab --resource-group $RESOURCE_GROUP \
  --revision $(az containerapp revision list --name voicelab --resource-group $RESOURCE_GROUP \
    --query "[?properties.active].name" -o tsv)
```

---

## When to Contact Support

If you've tried all troubleshooting steps and:
- Container App is running but Avatar still doesn't load
- Logs show errors you don't understand
- Environment variables are set correctly but application behaves incorrectly

Gather this information:
1. Output of: `az containerapp logs show --name voicelab --resource-group $RESOURCE_GROUP --tail 50`
2. Output of: `az containerapp show --name voicelab --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].env[].name" -o tsv`
3. Screenshot of the website error (if any)
4. Browser console errors (F12 → Console tab)

---

## Additional Resources

- [Azure Container Apps Troubleshooting](https://learn.microsoft.com/en-us/azure/container-apps/troubleshooting)
- [Azure CLI Container Apps Reference](https://learn.microsoft.com/en-us/cli/azure/containerapp)
- [Docker Build Context Best Practices](https://docs.docker.com/build/building/context/)
