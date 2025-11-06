# Azure Deployment Guide for Avatar Application

This guide documents how to deploy the Avatar application to Azure Container Apps using Azure Developer CLI (`azd`), including all the solutions to common deployment issues.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Azure Resources Setup](#azure-resources-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment Steps](#deployment-steps)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Manual Container App Configuration](#manual-container-app-configuration)
- [Verification Steps](#verification-steps)

---

## Prerequisites

### Required Tools

1. **Azure CLI** (`az`)
   ```powershell
   winget install -e --id Microsoft.AzureCLI
   ```

2. **Azure Developer CLI** (`azd`)
   ```powershell
   winget install -e --id Microsoft.Azd
   ```

3. **Docker Desktop** (for local testing)
   - Download from: https://www.docker.com/products/docker-desktop

4. **Git**
   ```powershell
   winget install -e --id Git.Git
   ```

### Required Azure Resources

Before deployment, you need to have or create the following Azure resources:

1. **Azure AI Foundry Project** (with GPT-4o deployment)
2. **Azure Speech Service**
3. **Bing Grounding Resource** (optional, for enhanced search)
4. **Azure AI Agent** (created in AI Foundry)

---

## Azure Resources Setup

### 1. Create Azure AI Foundry Project

```bash
# Set your resource group and location
RESOURCE_GROUP="rg-avatar-app"
LOCATION="eastus2"
AI_FOUNDRY_NAME="aifoundry-avatar-$(openssl rand -hex 6)"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create AI Foundry (Cognitive Services multi-service account)
az cognitiveservices account create \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind AIServices \
  --sku S0 \
  --location $LOCATION
```

### 2. Deploy GPT-4o Model

1. Go to [Azure AI Foundry Portal](https://ai.azure.com/)
2. Navigate to your project
3. Go to **Deployments** → **Create new deployment**
4. Select **gpt-4o** model
5. Set deployment name to `gpt-4o`
6. Deploy with default settings

### 3. Create Speech Service

```bash
SPEECH_SERVICE_NAME="speech-avatar-$(openssl rand -hex 6)"

az cognitiveservices account create \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind SpeechServices \
  --sku S0 \
  --location $LOCATION
```

### 4. Create Azure AI Agent

1. In Azure AI Foundry Portal, go to your project
2. Navigate to **Agents** section
3. Click **Create Agent**
4. Configure the agent with your requirements
5. **Save the Agent ID** (format: `asst_xxxxxxxxxxxxxxxxxxxxx`)

### 5. Create Bing Grounding Resource (Optional)

```bash
BING_RESOURCE_NAME="r-bing-avatar"

az cognitiveservices account create \
  --name $BING_RESOURCE_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind Bing.Search.v7 \
  --sku S1 \
  --location global
```

---

## Environment Configuration

### 1. Initialize Azure Developer CLI

```bash
cd voicelive-api-salescoach
azd init
```

When prompted:
- Environment name: Choose a name (e.g., `dev`, `prod`)
- Subscription: Select your Azure subscription
- Location: Choose region (e.g., `eastus2`)

### 2. Set Environment Variables

You need to configure the following environment variables in `azd`:

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Get resource endpoints and keys
AI_FOUNDRY_ENDPOINT=$(az cognitiveservices account show \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

SPEECH_REGION=$(az cognitiveservices account show \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query location -o tsv)

PROJECT_ENDPOINT="${AI_FOUNDRY_ENDPOINT}api/projects/YOUR-PROJECT-NAME"

# Set azd environment variables
azd env set AZURE_SUBSCRIPTION_ID "$SUBSCRIPTION_ID"
azd env set AZURE_LOCATION "$LOCATION"
azd env set AZURE_RESOURCE_GROUP "$RESOURCE_GROUP"

# AI Services configuration
azd env set azureOpenAiEndpoint "$AI_FOUNDRY_ENDPOINT"
azd env set projectEndpoint "$PROJECT_ENDPOINT"
azd env set modelDeploymentName "gpt-4o"
azd env set azureSpeechRegion "$SPEECH_REGION"
azd env set azureAiResourceName "$AI_FOUNDRY_NAME"
azd env set azureAiRegion "$LOCATION"
azd env set azureAiProjectName "YOUR-PROJECT-NAME"

# Agent configuration
azd env set useAzureAiAgents "true"
azd env set agentId "YOUR-AGENT-ID"  # From AI Foundry

# Bing Grounding (if using)
azd env set bingGroundingResourceName "$BING_RESOURCE_NAME"
azd env set bingGroundingResourceKey "YOUR-BING-KEY"

# Avatar configuration
azd env set azureVoiceName "en-US-AndrewMultilingualNeural"
azd env set azureSpeechLanguage "ar-SA,en-US"
azd env set azureAvatarCharacter "jeff"
azd env set azureAvatarStyle "business"

# Transcription settings
azd env set azureInputTranscriptionModel "azure-speech"
azd env set azureInputTranscriptionLanguage "ar-SA,en-US"
azd env set azureInputNoiseReductionType "azure_deep_noise_suppression"
azd env set azureVoiceType "azure-standard"
```

---

## Deployment Steps

### 1. Verify Project Structure

Ensure your `azure.yaml` (in root directory) is correctly configured:

```yaml
name: voicelive-api-salescoach
metadata:
  template: voicelive-api-salescoach
services:
  voicelab:
    project: voicelive-api-salescoach/backend
    language: py
    host: containerapp
    docker:
      path: ../Dockerfile
      context: ../
      remoteBuild: true
```

**Critical Points:**
- `project` must point to `voicelive-api-salescoach/backend` (not just `backend`)
- `docker.context` must be `../` to include both frontend and backend
- `remoteBuild: true` for Azure Container Registry build

### 2. Verify .dockerignore

Your `voicelive-api-salescoach/.dockerignore` should exclude unnecessary files:

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
.github/
.vscode/
.azuredevops/
.env
.env.local
*.log
```

**Important:** Use `**/node_modules/` pattern to exclude all node_modules directories recursively.

### 3. Deploy to Azure

```bash
# From the root directory (Avatar IP/)
azd up
```

This command will:
1. Provision Azure resources (Container Registry, Container App Environment, Container App)
2. Build the Docker image remotely in Azure Container Registry
3. Deploy the container to Azure Container Apps

**Expected Duration:** 10-15 minutes for first deployment

---

## Common Issues and Solutions

### Issue 1: "The directory name is invalid" Error

**Problem:** Docker build fails with directory path error.

**Solution:** Ensure `azure.yaml` has correct project path:
```yaml
project: voicelive-api-salescoach/backend  # NOT just "backend"
```

### Issue 2: "exec format error" (Platform Mismatch)

**Problem:** Container built for wrong architecture (ARM64 vs AMD64).

**Solution:** Azure Container Registry automatically builds for linux/amd64. Do NOT add `--platform` flags to Dockerfile as they cause warnings and are unnecessary with remote build.

### Issue 3: Slow Remote Build (Large Context)

**Problem:** Build context is 289 MB with 33,528 files due to node_modules.

**Solution:** Update `.dockerignore` with proper patterns:
```
**/node_modules/
frontend/node_modules/
backend/venv/
```

### Issue 4: Avatar Not Loading After Deployment

**Problem:** Container App deployed successfully but Avatar doesn't appear on website.

**Root Cause:** Environment variables not applied to Container App.

**Solution:** See [Manual Container App Configuration](#manual-container-app-configuration) section below.

### Issue 5: Bicep Deployment Not Updating Container App

**Problem:** Running `azd up` doesn't create new Container App revision with updated environment variables.

**Explanation:** Azure Container Apps may not trigger a new revision when only Bicep-defined environment variables change, especially if the container image hasn't changed.

**Solution:** Use manual `az containerapp update` command (see below).

---

## Manual Container App Configuration

If `azd up` completes but the Avatar still doesn't work, you need to manually configure the Container App environment variables and secrets.

### Step 1: Create Secrets

```bash
# Get API keys
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

# Set secrets in Container App
az containerapp secret set \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    "ai-foundry-api-key=$AI_KEY" \
    "speech-api-key=$SPEECH_KEY" \
    "bing-grounding-api-key=$BING_KEY"
```

### Step 2: Update Environment Variables

```bash
# Get values from azd environment
AZURE_OPENAI_ENDPOINT=$(azd env get-values | grep AZURE_OPENAI_ENDPOINT | cut -d'=' -f2 | tr -d '"')
PROJECT_ENDPOINT=$(azd env get-values | grep PROJECT_ENDPOINT | cut -d'=' -f2 | tr -d '"')
AGENT_ID=$(azd env get-values | grep AGENT_ID | cut -d'=' -f2 | tr -d '"')
SPEECH_REGION=$(azd env get-values | grep AZURE_SPEECH_REGION | cut -d'=' -f2 | tr -d '"')
SUBSCRIPTION_ID=$(azd env get-values | grep AZURE_SUBSCRIPTION_ID | cut -d'=' -f2 | tr -d '"')

# Update Container App with all environment variables
az containerapp update \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT" \
    "AZURE_OPENAI_API_KEY=secretref:ai-foundry-api-key" \
    "PROJECT_ENDPOINT=$PROJECT_ENDPOINT" \
    "MODEL_DEPLOYMENT_NAME=gpt-4o" \
    "AZURE_SPEECH_KEY=secretref:speech-api-key" \
    "AZURE_SPEECH_REGION=$SPEECH_REGION" \
    "AZURE_AI_RESOURCE_NAME=$AI_FOUNDRY_NAME" \
    "AZURE_AI_REGION=$LOCATION" \
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

**Note:** This command creates a new Container App revision with all environment variables properly configured.

---

## Verification Steps

### 1. Check Container App Revisions

```bash
az containerapp revision list \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Created:properties.createdTime, Active:properties.active}" \
  -o table
```

You should see a new revision created after the manual update.

### 2. Verify Environment Variables

```bash
az containerapp show \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env[].name" \
  -o tsv
```

Expected environment variables (27 total):
- APPLICATIONINSIGHTS_CONNECTION_STRING
- AZURE_CLIENT_ID
- PORT
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- PROJECT_ENDPOINT
- MODEL_DEPLOYMENT_NAME
- AZURE_SPEECH_KEY
- AZURE_SPEECH_REGION
- AZURE_AI_RESOURCE_NAME
- AZURE_AI_REGION
- AZURE_AI_PROJECT_NAME
- USE_AZURE_AI_AGENTS
- AGENT_ID
- BING_GROUNDING_RESOURCE_NAME
- BING_GROUNDING_RESOURCE_KEY
- BING_GROUNDING_CONFIG_ID
- AZURE_VOICE_NAME
- AZURE_SPEECH_LANGUAGE
- AZURE_AVATAR_CHARACTER
- AZURE_AVATAR_STYLE
- AZURE_INPUT_TRANSCRIPTION_MODEL
- AZURE_INPUT_TRANSCRIPTION_LANGUAGE
- AZURE_INPUT_NOISE_REDUCTION_TYPE
- AZURE_VOICE_TYPE
- SUBSCRIPTION_ID
- RESOURCE_GROUP_NAME

### 3. Check Avatar Configuration

```bash
az containerapp show \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env[?name=='AZURE_VOICE_NAME' || name=='AZURE_AVATAR_CHARACTER' || name=='AZURE_AVATAR_STYLE' || name=='AZURE_SPEECH_LANGUAGE'].{Name:name,Value:value}" \
  -o table
```

Expected output:
```
Name                    Value
----------------------  ------------------------------
AZURE_VOICE_NAME        en-US-AndrewMultilingualNeural
AZURE_SPEECH_LANGUAGE   ar-SA,en-US
AZURE_AVATAR_CHARACTER  jeff
AZURE_AVATAR_STYLE      business
```

### 4. Check Application Logs

```bash
az containerapp logs show \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --tail 30
```

Look for these success indicators:
```
pre-configured Azure AI Foundry agent: asst_xxxxxxxxxxxxxxxxxxxxx
initialized with Azure AI Agent Service support
initialized with endpoint: https://...
scenarios loaded: 4
evaluation scenarios loaded: 4
Voice Live Demo on http://0.0.0.0:8000
```

### 5. Test API Endpoint

```bash
# Get Container App URL
CONTAINER_APP_URL=$(az containerapp show \
  --name voicelab \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

# Test config endpoint
curl https://$CONTAINER_APP_URL/api/config
```

Expected response:
```json
{"proxy_enabled":true,"ws_endpoint":"/ws/voice"}
```

### 6. Access the Application

Open your browser and navigate to:
```
https://<your-container-app-url>
```

The Avatar (jeff character with business style) should appear and respond with Andrew Multilingual voice in both Arabic and English.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Apps                      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Container App: voicelab                  │  │
│  │                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐                 │  │
│  │  │   Frontend   │  │   Backend    │                 │  │
│  │  │ (React/Vite) │  │ (Flask/Python)│                 │  │
│  │  └──────────────┘  └──────────────┘                 │  │
│  │                                                        │  │
│  │  Environment Variables:                               │  │
│  │  - AZURE_OPENAI_ENDPOINT                             │  │
│  │  - AGENT_ID                                          │  │
│  │  - AZURE_VOICE_NAME                                  │  │
│  │  - AZURE_AVATAR_CHARACTER                            │  │
│  │  + 23 more...                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌────────────┐ ┌────────────┐
    │ Azure AI     │ │   Speech   │ │   Bing     │
    │ Foundry      │ │  Service   │ │ Grounding  │
    │              │ │            │ │            │
    │ - GPT-4o     │ │ - Andrew   │ │ - Search   │
    │ - Agent      │ │   Voice    │ │   API      │
    └──────────────┘ └────────────┘ └────────────┘
```

---

## Summary of Critical Configuration

### Files That Must Be Correct

1. **azure.yaml** (root directory)
   - `project: voicelive-api-salescoach/backend`
   - `docker.context: ../`
   - `remoteBuild: true`

2. **.dockerignore** (voicelive-api-salescoach/)
   - Must exclude `**/node_modules/`
   - Must exclude `backend/venv/`

3. **Bicep files** (infra/)
   - `main.bicep` must accept existing resource parameters
   - `resources.bicep` must configure all environment variables
   - **Note:** May require manual Container App update

### Environment Variables Checklist

Essential variables that MUST be set:
- ✅ AZURE_OPENAI_ENDPOINT
- ✅ AZURE_OPENAI_API_KEY (as secretRef)
- ✅ PROJECT_ENDPOINT
- ✅ AGENT_ID
- ✅ AZURE_SPEECH_KEY (as secretRef)
- ✅ AZURE_SPEECH_REGION
- ✅ AZURE_VOICE_NAME
- ✅ AZURE_AVATAR_CHARACTER
- ✅ AZURE_AVATAR_STYLE
- ✅ USE_AZURE_AI_AGENTS=true

---

## Troubleshooting Commands

```bash
# Check if container is running
az containerapp show --name voicelab --resource-group $RESOURCE_GROUP --query "properties.runningStatus"

# Get container app URL
az containerapp show --name voicelab --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv

# Stream logs
az containerapp logs show --name voicelab --resource-group $RESOURCE_GROUP --follow

# List all revisions
az containerapp revision list --name voicelab --resource-group $RESOURCE_GROUP -o table

# Restart container app
az containerapp revision restart --name voicelab --resource-group $RESOURCE_GROUP --revision <revision-name>
```

---

## Support and Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-services/)
- [Azure Speech Service Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/)

---

## License

See [LICENSE.md](LICENSE.md) for details.
