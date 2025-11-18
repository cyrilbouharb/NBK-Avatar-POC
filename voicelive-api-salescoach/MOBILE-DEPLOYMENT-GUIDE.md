# Mobile Backend Deployment Guide

## 🎯 Overview

This guide covers deploying the **mobile-backend-only** branch of the NBK Banking Voice Backend to Azure Container Apps.

**Key Differences from Main Branch**:
- ✅ No frontend - backend only
- ✅ Auto-initializes with NBK Banking scenario
- ✅ WebSocket-only API for mobile integration
- ✅ Smaller container size and faster builds
- ✅ Simplified configuration

---

## 📋 Prerequisites

1. **Azure CLI** installed and authenticated
2. **Azure Developer CLI (azd)** installed
3. **Azure subscription** with permissions to create resources
4. **Git** installed

---

## 🚀 Step-by-Step Deployment

### Step 1: Clone and Switch to Mobile Backend Branch

```bash
# Clone the repository
git clone <your-repo-url>
cd voicelive-api-salescoach

# Switch to mobile backend branch
git checkout mobile-backend-only
```

### Step 2: Authenticate with Azure

```bash
# Login to Azure CLI
az login

# Login to Azure Developer CLI
azd auth login
```

### Step 3: Initialize azd Environment

```bash
# Initialize azd (if not already initialized)
azd init

# Follow prompts:
# - Environment name: e.g., "nbk-voice-mobile"
# - Azure subscription: Select your subscription
# - Azure location: e.g., "eastus" or "swedencentral"
```

### Step 4: Deploy Infrastructure and Application

```bash
# Deploy everything (infrastructure + container)
azd up
```

This will:
- ✅ Create Resource Group
- ✅ Deploy Azure AI Services (GPT-4o)
- ✅ Deploy Azure Speech Services
- ✅ Create Container Registry
- ✅ Build and push Docker image
- ✅ Create Container App
- ✅ Configure all environment variables

**Deployment time**: ~15-20 minutes

### Step 5: Get Deployment Output

After deployment completes, note these values:

```bash
# Get Container App name
azd env get-value AZURE_CONTAINER_APP_NAME

# Get Resource Group name
azd env get-value AZURE_ENV_NAME

# Get Service URL
azd env get-value SERVICE_VOICELAB_URI
```

Your WebSocket endpoint will be:
```
wss://<SERVICE_VOICELAB_URI>/ws/voice
```

---

## 🤖 Configure Azure AI Foundry Agent

### Step 1: Create Agent in Azure AI Foundry

1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Select your AI Services resource (created by deployment)
3. Navigate to **Agents** → **Create Agent**
4. Name: `NBK Banking Customer Service`
5. Model: Use `gpt-4o` (already deployed)

### Step 2: Add Agent Instructions

Paste these instructions:

```text
CRITICAL INTERACTION GUIDELINES FOR NBK BANKING CUSTOMER SERVICE:
- You are a helpful and professional NBK (National Bank of Kuwait) customer service representative
- Keep responses SHORT and conversational (3-4 sentences max, as if speaking on phone)
- Provide accurate information about NBK banking services, products, and policies
- Be courteous, patient, and empathetic with customers
- Use natural speech patterns appropriate for customer service
- Always prioritize customer security and privacy
- If you don't know specific account details, guide customers to secure channels
- Speak naturally in either Arabic or English based on customer's language preference
- For Arabic speakers, use clear Modern Standard Arabic that's accessible to Kuwaiti dialect speakers
- Show genuine care and professionalism in every interaction
- Use the Bing Custom Search tool to find accurate, up-to-date information from NBK's official website
- Always cite sources when providing information from NBK website
- If information is not available, politely acknowledge and direct customer to appropriate NBK channels
```

### Step 3: Configure Tools (Optional)

If you have Bing Custom Search configured:
1. Add **Bing Custom Search** tool
2. Configure with your NBK search instance

### Step 4: Copy Agent ID

After creating the agent:
1. Click on the agent to view details
2. Copy the **Agent ID** (format: `asst_xxxxxxxxxxxxxxxxxxxxx`)

---

## ⚙️ Configure Container App with Agent ID

### Using PowerShell

```powershell
# Set variables
$APP_NAME = azd env get-value AZURE_CONTAINER_APP_NAME
$RESOURCE_GROUP = "rg-$(azd env get-value AZURE_ENV_NAME)"
$AGENT_ID = "asst_xxxxxxxxxxxxx"  # ⚠️ Replace with your Agent ID

# Update Container App
az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars "AGENT_ID=$AGENT_ID" "USE_AZURE_AI_AGENTS=true"
```

### Using Bash

```bash
# Set variables
APP_NAME=$(azd env get-value AZURE_CONTAINER_APP_NAME)
RESOURCE_GROUP="rg-$(azd env get-value AZURE_ENV_NAME)"
AGENT_ID="asst_xxxxxxxxxxxxx"  # ⚠️ Replace with your Agent ID

# Update Container App
az containerapp update \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --set-env-vars "AGENT_ID=$AGENT_ID" "USE_AZURE_AI_AGENTS=true"
```

### Verify Configuration

```bash
# Check environment variables
az containerapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.template.containers[0].env" \
  --output table
```

Look for:
- `AGENT_ID`: Should show your agent ID
- `USE_AZURE_AI_AGENTS`: Should be `true`

---

## ✅ Verify Deployment

### 1. Check Health Endpoint

```bash
SERVICE_URL=$(azd env get-value SERVICE_VOICELAB_URI)
curl "${SERVICE_URL}/api/health"
```

Expected response:
```json
{
  "status": "healthy",
  "service": "NBK Banking Voice Backend",
  "websocket_endpoint": "/ws/voice"
}
```

### 2. Check Configuration Endpoint

```bash
curl "${SERVICE_URL}/api/config"
```

Expected response:
```json
{
  "proxy_enabled": true,
  "ws_endpoint": "/ws/voice",
  "mode": "mobile_backend",
  "scenario": "nbk-banking"
}
```

### 3. Test WebSocket Connection

Using `wscat`:

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
SERVICE_URL=$(azd env get-value SERVICE_VOICELAB_URI)
WS_URL=$(echo $SERVICE_URL | sed 's/https/wss/')
wscat -c "${WS_URL}/ws/voice"
```

You should receive:
```json
{"type":"proxy.connected","message":"Connected to Azure Voice API"}
```

---

## 📊 Monitor and Debug

### View Container App Logs

**Azure Portal**:
1. Go to Azure Portal → Resource Groups
2. Select your resource group
3. Open the Container App
4. Navigate to **Monitoring** → **Log stream**

**Azure CLI**:
```bash
az containerapp logs show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --follow
```

### View Application Insights

```bash
# Get Application Insights connection string
az monitor app-insights component show \
  --app <app-insights-name> \
  --resource-group "$RESOURCE_GROUP" \
  --query "connectionString"
```

Access logs in Azure Portal → Application Insights → Logs

### Common Issues

**Issue**: Container App not starting  
**Solution**: Check logs for Python/dependency errors

**Issue**: WebSocket connection fails  
**Solution**: Verify ingress is enabled and external

**Issue**: Agent not responding  
**Solution**: Verify `AGENT_ID` and `USE_AZURE_AI_AGENTS` are set correctly

---

## 🔄 Update and Redeploy

### Update Code

```bash
# Make code changes
git add .
git commit -m "Your changes"

# Redeploy only the application (faster)
azd deploy
```

### Update Infrastructure

```bash
# Modify bicep files if needed
# Then redeploy everything
azd up
```

### Update Agent Configuration

Simply update the environment variables without redeploying:

```bash
az containerapp update \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --set-env-vars "AGENT_ID=<new-agent-id>"
```

---

## 🗑️ Cleanup Resources

### Delete Everything

```bash
# Delete all Azure resources
azd down --purge

# Remove local environment
azd env delete
```

### Delete Specific Resources

```bash
# Delete just the Container App
az containerapp delete \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP"
```

---

## 📝 Environment Variables Reference

All environment variables are automatically configured by `azd up`. Here's the complete list:

| Variable | Description | Set By |
|----------|-------------|--------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | azd |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | azd |
| `AZURE_SPEECH_KEY` | Azure Speech Services key | azd |
| `AZURE_SPEECH_REGION` | Azure region for Speech | azd |
| `MODEL_DEPLOYMENT_NAME` | GPT model deployment name | azd |
| `AGENT_ID` | Azure AI Foundry Agent ID | Manual |
| `USE_AZURE_AI_AGENTS` | Enable Azure AI Agents | Manual |
| `AZURE_AI_RESOURCE_NAME` | AI Services resource name | azd |
| `AZURE_VOICE_NAME` | TTS voice name | azd |
| `AZURE_SPEECH_LANGUAGE` | Supported languages | azd |
| `PORT` | Application port | azd |

---

## 🎉 Next Steps

After successful deployment:

1. **Share WebSocket endpoint** with mobile team
2. **Provide mobile integration guide**: See `MOBILE-INTEGRATION-GUIDE.md`
3. **Test with mobile app** in development
4. **Monitor usage** via Application Insights
5. **Scale as needed** based on traffic

---

## 📞 Support

For deployment issues:
1. Check Container App logs
2. Review Application Insights
3. Verify all environment variables are set
4. Consult Azure documentation

---

**Deployment Complete! 🚀**
