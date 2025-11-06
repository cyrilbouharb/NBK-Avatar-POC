# Azure Deployment Guide for NBK Avatar Application

This comprehensive guide walks you through deploying the NBK Avatar application to Azure Container Apps from scratch on a brand new Azure subscription.

> **⚠️ CRITICAL**: You must create Azure AI resources FIRST before running `azd up`. The deployment does NOT automatically create AI Foundry or Speech services.

## Quick Navigation

- [Prerequisites](#prerequisites) - Tools and accounts needed
- [Step 1: Create Azure AI Resources](#step-1-create-azure-ai-resources) - **DO THIS FIRST**
- [Step 2: Configure Azure AI Agent](#step-2-configure-azure-ai-agent) - Set up NBK customer service agent
- [Step 3: Set Environment Variables](#step-3-set-environment-variables) - Configure deployment
- [Step 4: Deploy Container App](#step-4-deploy-container-app) - Run `azd up`
- [Step 5: Configure Container App](#step-5-configure-container-app) - **REQUIRED** manual step
- [Verification](#verification-steps) - Test your deployment
- [Troubleshooting](#troubleshooting) - Common issues and fixes

---

## Prerequisites

### Required Tools

Install these tools before starting (estimated time: 10 minutes):

**1. Azure CLI**
```powershell
# Windows
winget install -e --id Microsoft.AzureCLI

# Verify installation
az --version
```

**2. Azure Developer CLI**
```powershell
# Windows
winget install -e --id Microsoft.Azd

# Verify installation
azd version
```

**3. Git**
```powershell
# Windows
winget install -e --id Git.Git

# Verify installation
git --version
```

**4. Login to Azure**
```bash
# Login with Azure CLI
az login

# Login with Azure Developer CLI
azd auth login
```

### Azure Subscription Requirements

- Active Azure subscription with Owner or Contributor permissions
- Estimated monthly cost: $50-150 (depending on usage)
  - Azure AI Services (S0 tier): ~$10-50/month
  - Speech Services (S0 tier): ~$10-50/month
  - Container Apps: ~$20-50/month (based on usage)
  - Container Registry: ~$5/month
  - Bing Search (optional): ~$5-20/month

---

## Step 1: Create Azure AI Resources

> **⚠️ DO THIS BEFORE RUNNING `azd up`**
> 
> The `azd up` command deploys Container App infrastructure but does NOT create:
> - Azure AI Foundry (Cognitive Services)
> - Speech Service
> - Azure AI Agent
> 
> You must create these manually first.

### 1.1 Set Variables for Your Deployment

Choose unique resource names (they must be globally unique in Azure):

**PowerShell:**
```powershell
# Set your preferences
$RESOURCE_GROUP = "rg-nbk-avatar"
$LOCATION = "eastus2"  # or your preferred region (use: az account list-locations -o table)

# Generate unique names
$AI_FOUNDRY_NAME = "aifoundry-nbk-$(Get-Random -Maximum 99999)"
$SPEECH_SERVICE_NAME = "speech-nbk-$(Get-Random -Maximum 99999)"
$BING_RESOURCE_NAME = "bing-nbk-$(Get-Random -Maximum 99999)"

# Get subscription ID
$SUBSCRIPTION_ID = (az account show --query id -o tsv)

# Display values
Write-Host "=== Your Deployment Configuration ===" -ForegroundColor Cyan
Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host "Location: $LOCATION"
Write-Host "AI Foundry: $AI_FOUNDRY_NAME"
Write-Host "Speech Service: $SPEECH_SERVICE_NAME"
Write-Host "Bing Resource: $BING_RESOURCE_NAME"
Write-Host "Subscription: $SUBSCRIPTION_ID"
Write-Host "=====================================" -ForegroundColor Cyan
```

**Bash/Linux:**
```bash
# Set your preferences
RESOURCE_GROUP="rg-nbk-avatar"
LOCATION="eastus2"  # or your preferred region (use: az account list-locations -o table)

# Generate unique names
AI_FOUNDRY_NAME="aifoundry-nbk-$RANDOM"
SPEECH_SERVICE_NAME="speech-nbk-$RANDOM"
BING_RESOURCE_NAME="bing-nbk-$RANDOM"

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Display values
echo "=== Your Deployment Configuration ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "AI Foundry: $AI_FOUNDRY_NAME"
echo "Speech Service: $SPEECH_SERVICE_NAME"
echo "Bing Resource: $BING_RESOURCE_NAME"
echo "Subscription: $SUBSCRIPTION_ID"
echo "====================================="
```

### 1.2 Create Resource Group

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

**✅ Verify:**
```bash
az group show --name $RESOURCE_GROUP
```

### 1.3 Create Azure AI Foundry (Cognitive Services)

This creates a multi-service Cognitive Services account that includes OpenAI capabilities.

```bash
az cognitiveservices account create \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind AIServices \
  --sku S0 \
  --location $LOCATION \
  --yes
```

**⏱️ Expected Time:** 2-3 minutes

**✅ Verify:**
```bash
az cognitiveservices account show \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:properties.provisioningState, Endpoint:properties.endpoint}" -o table
```

Should show: `State: Succeeded`

### 1.4 Deploy GPT-4o Model

> **⚠️ Important:** This step must be done in the Azure AI Foundry portal, not via CLI.

**Steps:**
1. Open [Azure AI Foundry Portal](https://ai.azure.com/)
2. Sign in with your Azure account
3. Click on **Your resources** → Find your AI Foundry resource (created in step 1.3)
4. Click on the resource to open it
5. In the left navigation, click **Deployments**
6. Click **+ Create new deployment**
7. Configure:
   - **Model**: Select `gpt-4o`
   - **Deployment name**: Enter `gpt-4o` (must be exactly this)
   - **Deployment type**: Standard
   - **Tokens per Minute Rate Limit**: 10K (or your preferred limit)
8. Click **Deploy**
9. **⏱️ Wait 2-5 minutes** for deployment to complete

**✅ Verify:**
- You should see `gpt-4o` deployment listed with status "Succeeded"

### 1.5 Create Speech Service

```bash
az cognitiveservices account create \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind SpeechServices \
  --sku S0 \
  --location $LOCATION \
  --yes
```

**⏱️ Expected Time:** 2-3 minutes

**✅ Verify:**
```bash
az cognitiveservices account show \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:properties.provisioningState, Region:location}" -o table
```

Should show: `State: Succeeded`

### 1.6 Create Bing Grounding Resource (Optional but Recommended)

This enables the agent to search NBK's website for accurate information.

```bash
az cognitiveservices account create \
  --name $BING_RESOURCE_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind Bing.Search.v7 \
  --sku S1 \
  --location global \
  --yes
```

**⏱️ Expected Time:** 1-2 minutes

**✅ Verify:**
```bash
az cognitiveservices account show \
  --name $BING_RESOURCE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "{Name:name, State:properties.provisioningState}" -o table
```

---

## Step 2: Configure Azure AI Agent

### 2.1 Create Agent in AI Foundry Portal

**Steps:**
1. Go to [Azure AI Foundry Portal](https://ai.azure.com/)
2. Select your AI Foundry resource
3. In the left navigation, click **Agents**
4. Click **+ New Agent**
5. Configure:
   - **Name**: `NBK Customer Service Agent`
   - **Deployment**: Select your `gpt-4o` deployment
   - **Description**: `Professional NBK customer service representative with bilingual support`

### 2.2 Set Agent Instructions

Copy and paste this into the **Instructions** field:

```
You are a professional customer service representative for NBK (National Bank of Kuwait).

Your role is to:
- Assist customers with inquiries about NBK banking services and products
- Provide information about accounts, cards, loans, investments, and digital banking
- Help customers understand NBK's services using information from the official NBK website
- Communicate clearly in both Arabic and English
- Maintain a professional, helpful, and courteous demeanor
- Ensure customer security by not asking for sensitive personal information
- Use the Bing Custom Search tool to find accurate information from NBK's public website

Language Support:
- For Arabic: Use clear Modern Standard Arabic (الفصحى) that Kuwaiti customers will understand easily
- For English: Use professional but friendly business English
- Detect and match the customer's preferred language automatically

Important Guidelines:
- Never ask for account numbers, passwords, PINs, or other sensitive credentials
- For account-specific inquiries, direct customers to secure channels (NBK app, visit branch, call secure line)
- Always cite your sources when providing information from NBK website
- If you're unsure about something, acknowledge it professionally and offer to connect customer with specialized support
- Be patient and empathetic, especially with customers who may be frustrated or confused
- Keep responses SHORT and conversational (3 sentences max, as if speaking on phone)

Common Topics You Can Help With:
- Information about NBK accounts (savings, current, salary accounts)
- Credit and debit cards (features, benefits, how to apply)
- Personal loans and financing options
- Investment products and wealth management services
- Digital banking (NBK Mobile app, online banking)
- Branch locations and working hours
- General banking procedures and requirements
- Customer service contact information

Remember: You represent NBK's commitment to excellent customer service. Be helpful, professional, and trustworthy.
```

### 2.3 Add Bing Search Tool (If Using)

1. Click **Add tool**
2. Select **Bing Custom Search**
3. Configure:
   - Resource: Select your Bing resource
   - Custom Configuration ID: (You'll configure this in Bing Custom Search portal)

### 2.4 Save and Copy Agent ID

1. Click **Create**
2. **⏱️ Wait 30-60 seconds** for agent to be created
3. **✅ CRITICAL:** Copy the **Agent ID** - it looks like `asst_xxxxxxxxxxxxxxxxxxxxx`
4. Save this ID - you'll need it in the next step

**PowerShell:**
```powershell
$AGENT_ID = "asst_xxxxxxxxxxxxxxxxxxxxx"  # Replace with your actual Agent ID
Write-Host "Agent ID saved: $AGENT_ID" -ForegroundColor Green
```

**Bash:**
```bash
AGENT_ID="asst_xxxxxxxxxxxxxxxxxxxxx"  # Replace with your actual Agent ID
echo "Agent ID saved: $AGENT_ID"
```

---

## Step 3: Set Environment Variables

### 3.1 Clone Repository

```bash
# Navigate to your projects directory
cd ~  # or your preferred directory

# Clone the repository
git clone <your-repo-url>
cd "Avatar IP"
```

### 3.2 Get Resource Endpoints and Keys

**PowerShell:**
```powershell
# Get AI Foundry endpoint
$AI_ENDPOINT = (az cognitiveservices account show `
  --name $AI_FOUNDRY_NAME `
  --resource-group $RESOURCE_GROUP `
  --query properties.endpoint -o tsv)

# Get Speech region
$SPEECH_REGION = (az cognitiveservices account show `
  --name $SPEECH_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query location -o tsv)

# Construct project endpoint
$PROJECT_NAME = "${AI_FOUNDRY_NAME}-project"
$PROJECT_ENDPOINT = "${AI_ENDPOINT}api/projects/${PROJECT_NAME}"

# Display for verification
Write-Host "=== Resource Configuration ===" -ForegroundColor Cyan
Write-Host "AI Endpoint: $AI_ENDPOINT"
Write-Host "Speech Region: $SPEECH_REGION"
Write-Host "Project Endpoint: $PROJECT_ENDPOINT"
Write-Host "Agent ID: $AGENT_ID"
Write-Host "==============================" -ForegroundColor Cyan
```

**Bash:**
```bash
# Get AI Foundry endpoint
AI_ENDPOINT=$(az cognitiveservices account show \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

# Get Speech region
SPEECH_REGION=$(az cognitiveservices account show \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query location -o tsv)

# Construct project endpoint
PROJECT_NAME="${AI_FOUNDRY_NAME}-project"
PROJECT_ENDPOINT="${AI_ENDPOINT}api/projects/${PROJECT_NAME}"

# Display for verification
echo "=== Resource Configuration ==="
echo "AI Endpoint: $AI_ENDPOINT"
echo "Speech Region: $SPEECH_REGION"
echo "Project Endpoint: $PROJECT_ENDPOINT"
echo "Agent ID: $AGENT_ID"
echo "=============================="
```

### 3.3 Initialize Azure Developer CLI

```bash
cd voicelive-api-salescoach
azd init
```

**When prompted:**
- **Environment name**: `dev` (or your preferred name like `prod`, `staging`)
- **Subscription**: Select your Azure subscription (should match where you created resources)
- **Location**: `eastus2` (MUST match the location where you created AI resources)

### 3.4 Configure All azd Environment Variables

Run all these commands to configure your deployment:

```bash
# Core Azure configuration
azd env set AZURE_SUBSCRIPTION_ID "$SUBSCRIPTION_ID"
azd env set AZURE_LOCATION "$LOCATION"
azd env set AZURE_RESOURCE_GROUP "$RESOURCE_GROUP"

# AI Foundry configuration
azd env set azureOpenAiEndpoint "$AI_ENDPOINT"
azd env set projectEndpoint "$PROJECT_ENDPOINT"
azd env set modelDeploymentName "gpt-4o"
azd env set azureAiResourceName "$AI_FOUNDRY_NAME"
azd env set azureAiRegion "$LOCATION"
azd env set azureAiProjectName "$PROJECT_NAME"

# Speech configuration
azd env set azureSpeechRegion "$SPEECH_REGION"
azd env set azureVoiceName "en-US-AndrewMultilingualNeural"
azd env set azureSpeechLanguage "ar-SA,en-US"

# Agent configuration
azd env set useAzureAiAgents "true"
azd env set agentId "$AGENT_ID"

# Avatar configuration
azd env set azureAvatarCharacter "jeff"
azd env set azureAvatarStyle "business"

# Transcription settings
azd env set azureInputTranscriptionModel "azure-speech"
azd env set azureInputTranscriptionLanguage "ar-SA,en-US"
azd env set azureInputNoiseReductionType "azure_deep_noise_suppression"
azd env set azureVoiceType "azure-standard"

# Bing Grounding (if created)
azd env set bingGroundingResourceName "$BING_RESOURCE_NAME"
```

**✅ Verify configuration:**
```bash
azd env get-values
```

You should see all variables listed.

---

## Step 4: Deploy Container App

> **📝 Note:** This step deploys Container App infrastructure (Container Registry, Container App Environment, Container App, Application Insights). It does NOT create AI services (you already did that in Step 1).

### 4.1 Run Deployment

```bash
azd up
```

**What this does:**
1. ✅ Provisions Container Registry
2. ✅ Provisions Container App Environment
3. ✅ Provisions Container App
4. ✅ Provisions Application Insights
5. ✅ Builds Docker image remotely in Azure Container Registry
6. ✅ Deploys container to Azure Container Apps

**⏱️ Expected Time:** 10-15 minutes (first deployment)

**Expected Output:**
```
Provisioning Azure resources can take some time...
  (✓) Completed: Resource group: rg-nbk-avatar
  (✓) Completed: Container Registry (cr...)
  (✓) Completed: Container App Environment
  (✓) Completed: Log Analytics Workspace
  (✓) Completed: Application Insights
  (✓) Completed: Container App (voicelab)

Packaging services (azd package)
  (✓) Completed: Packaging service voicelab

Deploying services (release):
  (✓) Completed: Deploying service voicelab
    - Endpoint: https://voicelab.<random-id>.<region>.azurecontainerapps.io

SUCCESS: Your application has been deployed!
```

### 4.2 Get Deployment Information

```bash
# Get Container App name
APP_NAME=$(azd env get-value AZURE_CONTAINER_APPS_NAME)

# Get Container App URL
APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Application URL: https://$APP_URL"
```

**🔗 Save this URL** - you'll use it to access your application.

---

## Step 5: Configure Container App

> **⚠️ CRITICAL STEP - DO NOT SKIP**
> 
> The `azd up` command does NOT automatically configure environment variables in the Container App. This is a known limitation. You MUST manually configure them.

### Why This Step is Required

Azure Developer CLI has a limitation where environment variables defined in Bicep templates are not automatically applied to running Container App revisions. After `azd up`, your Container App will have only ~3 default environment variables instead of the 27 required for the Avatar to work.

### 5.1 Get API Keys

**PowerShell:**
```powershell
# Get AI Foundry API key
$AI_KEY = (az cognitiveservices account keys list `
  --name $AI_FOUNDRY_NAME `
  --resource-group $RESOURCE_GROUP `
  --query key1 -o tsv)

# Get Speech API key
$SPEECH_KEY = (az cognitiveservices account keys list `
  --name $SPEECH_SERVICE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query key1 -o tsv)

# Get Bing key (if created)
$BING_KEY = (az cognitiveservices account keys list `
  --name $BING_RESOURCE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query key1 -o tsv)

# Verify keys retrieved
Write-Host "=== API Keys Retrieved ===" -ForegroundColor Cyan
Write-Host "AI Foundry Key: $($AI_KEY.Substring(0,8))..." -ForegroundColor Green
Write-Host "Speech Key: $($SPEECH_KEY.Substring(0,8))..." -ForegroundColor Green
Write-Host "Bing Key: $($BING_KEY.Substring(0,8))..." -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Cyan
```

**Bash:**
```bash
# Get AI Foundry API key
AI_KEY=$(az cognitiveservices account keys list \
  --name $AI_FOUNDRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

# Get Speech API key
SPEECH_KEY=$(az cognitiveservices account keys list \
  --name $SPEECH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

# Get Bing key (if created)
BING_KEY=$(az cognitiveservices account keys list \
  --name $BING_RESOURCE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

# Verify keys retrieved
echo "=== API Keys Retrieved ==="
echo "AI Foundry Key: ${AI_KEY:0:8}..."
echo "Speech Key: ${SPEECH_KEY:0:8}..."
echo "Bing Key: ${BING_KEY:0:8}..."
echo "=========================="
```

### 5.2 Set Container App Secrets

```bash
az containerapp secret set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets \
    ai-foundry-api-key="$AI_KEY" \
    speech-api-key="$SPEECH_KEY" \
    bing-grounding-api-key="$BING_KEY"
```

**✅ Verify:**
```bash
az containerapp secret list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].name" -o table
```

Should show:
```
Result
-----------------------
ai-foundry-api-key
speech-api-key
bing-grounding-api-key
```

### 5.3 Update Container App with All Environment Variables

> **⚠️ Important:** This command creates a NEW revision of your Container App. The new revision will include all 27 environment variables.

```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    AZURE_OPENAI_ENDPOINT="$AI_ENDPOINT" \
    PROJECT_ENDPOINT="$PROJECT_ENDPOINT" \
    MODEL_DEPLOYMENT_NAME="gpt-4o" \
    AZURE_AI_RESOURCE_NAME="$AI_FOUNDRY_NAME" \
    AZURE_AI_REGION="$LOCATION" \
    AZURE_AI_PROJECT_NAME="$PROJECT_NAME" \
    AZURE_SPEECH_REGION="$SPEECH_REGION" \
    AZURE_VOICE_NAME="en-US-AndrewMultilingualNeural" \
    AZURE_SPEECH_LANGUAGE="ar-SA,en-US" \
    USE_AZURE_AI_AGENTS="true" \
    AGENT_ID="$AGENT_ID" \
    AZURE_AVATAR_CHARACTER="jeff" \
    AZURE_AVATAR_STYLE="business" \
    AZURE_INPUT_TRANSCRIPTION_MODEL="azure-speech" \
    AZURE_INPUT_TRANSCRIPTION_LANGUAGE="ar-SA,en-US" \
    AZURE_INPUT_NOISE_REDUCTION_TYPE="azure_deep_noise_suppression" \
    AZURE_VOICE_TYPE="azure-standard" \
    AZURE_AI_FOUNDRY_API_KEY=secretref:ai-foundry-api-key \
    AZURE_SPEECH_API_KEY=secretref:speech-api-key \
    BING_GROUNDING_API_KEY=secretref:bing-grounding-api-key \
    BING_GROUNDING_RESOURCE_NAME="$BING_RESOURCE_NAME"
```

**⏱️ Expected Time:** 2-3 minutes for new revision to deploy

### 5.4 Verify New Revision Created

```bash
az containerapp revision list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Active:properties.active, Health:properties.healthState, Created:properties.createdTime}" \
  -o table
```

**Expected output:**
```
Name                        Active    Health    Created
--------------------------  --------  --------  -------------------------
voicelab--0000002           True      Healthy   2024-01-15T10:30:00+00:00
voicelab--0000001           False     Healthy   2024-01-15T10:15:00+00:00
```

The newest revision should be `Active: True` and `Health: Healthy`.

### 5.5 Wait for Deployment to Complete

```bash
# Wait 2-3 minutes, then check revision health
az containerapp revision show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --revision $(az containerapp revision list --name $APP_NAME --resource-group $RESOURCE_GROUP --query "[?properties.active].name" -o tsv) \
  --query "{Name:name, Health:properties.healthState, Replicas:properties.replicas}" -o table
```

Should show: `Health: Healthy`, `Replicas: 1` (or more)

---

## Verification Steps

### 1. Check Application Health Endpoint

```bash
curl https://$APP_URL/api/config
```

**Expected Response:**
```json
{
  "azure_openai_endpoint": "https://aifoundry-nbk-xxxxx.openai.azure.com/",
  "project_endpoint": "https://aifoundry-nbk-xxxxx.openai.azure.com/api/projects/aifoundry-nbk-xxxxx-project",
  "model_deployment_name": "gpt-4o",
  "azure_voice_name": "en-US-AndrewMultilingualNeural",
  "azure_avatar_character": "jeff",
  "azure_avatar_style": "business",
  "azure_speech_language": "ar-SA,en-US",
  "use_azure_ai_agents": true
}
```

**✅ If you see this:** Configuration is correct!

**❌ If you see errors:** Check Container App logs (see Troubleshooting section)

### 2. Test Avatar in Browser

1. Open your browser
2. Navigate to: `https://$APP_URL`
3. You should see the Avatar application homepage
4. Click **Start** or **Begin** button
5. **Expected behavior:**
   - Avatar character "Jeff" appears (business style)
   - Microphone access requested
   - You can speak in Arabic or English
   - Avatar responds with Andrew Multilingual voice

**Test in Arabic:**
```
"مرحبا، أريد معلومات عن حساب التوفير"
(Hello, I want information about savings accounts)
```

**Test in English:**
```
"Hello, I need help with NBK credit cards"
```

### 3. Check Container App Logs

```bash
# Stream live logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Or view recent logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100
```

**✅ Expected log entries:**
```
Starting Flask application...
Azure OpenAI endpoint configured: https://...
Speech region configured: eastus2
Agent ID configured: asst_...
WebSocket connection established
```

### 4. Verify All Environment Variables Set

```bash
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env" -o table
```

You should see **27 environment variables** listed (not just 3).

---

## Troubleshooting

### Avatar Not Loading

**Symptoms:**
- Application loads but no Avatar appears
- Browser console shows errors

**Solutions:**

**1. Verify all environment variables:**
```bash
# Count environment variables
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env | length(@)" -o tsv
```

Should return: `27` or more

**2. Check Container App logs:**
```bash
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 50
```

Look for errors like:
- `Missing environment variable: AGENT_ID`
- `Failed to initialize Azure OpenAI client`
- `Speech service authentication failed`

**3. Verify API keys work:**
```bash
# Test AI Foundry endpoint
curl -X POST "$AI_ENDPOINT/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview" \
  -H "api-key: $AI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

Should return a JSON response (not 401 Unauthorized).

**4. Re-apply environment variables:**

If environment variables are missing, re-run Step 5.3.

---

### Build Failures

**Symptoms:**
- `azd up` fails during build phase
- "exec format error" or "platform mismatch"

**Solutions:**

**1. Ensure `remoteBuild: true`:**

Check `azure.yaml` (in root directory):
```yaml
services:
  voicelab:
    docker:
      remoteBuild: true  # Must be true
```

**2. Verify `.dockerignore`:**

Check `voicelive-api-salescoach/.dockerignore` includes:
```
**/node_modules/
frontend/node_modules/
backend/venv/
backend/__pycache__/
```

**3. Check Dockerfile has no platform flags:**

In `voicelive-api-salescoach/backend/Dockerfile`, ensure there are NO `--platform` flags:
```dockerfile
# ✅ Correct
FROM node:20-alpine AS frontend-builder

# ❌ Wrong
FROM --platform=linux/amd64 node:20-alpine AS frontend-builder
```

---

### Slow Build (15+ minutes)

**Symptoms:**
- Build context upload takes very long
- Shows "Sending build context: 289 MB"

**Solution:**

Update `.dockerignore` to exclude `node_modules`:

```bash
cd voicelive-api-salescoach
cat > .dockerignore << 'EOF'
**/node_modules/
frontend/node_modules/
backend/venv/
backend/__pycache__/
**/__pycache__/
**/*.pyc
.git/
.github/
.vscode/
.env
.env.local
*.log
EOF
```

Then re-run `azd up`.

---

### "Agent Not Found" or Agent Errors

**Symptoms:**
- Avatar loads but doesn't respond
- Logs show "Agent asst_xxx not found"

**Solutions:**

**1. Verify Agent ID is correct:**
```bash
# Get current Agent ID from Container App
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.template.containers[0].env[?name=='AGENT_ID'].value" -o tsv
```

**2. List agents in AI Foundry:**
- Go to https://ai.azure.com/
- Select your project
- Go to **Agents**
- Verify agent exists and copy the correct ID

**3. Update Agent ID if wrong:**
```bash
# Set correct Agent ID
AGENT_ID="asst_xxxxxxxxxxxxxxxxxxxxx"  # Your correct agent ID

# Update Container App
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars AGENT_ID="$AGENT_ID"
```

---

### Resources Not in Same Region

**Symptoms:**
- Higher latency
- Errors about cross-region communication

**Solution:**

Ensure all resources are in the same region:
```bash
# Check all resource locations
az resource list \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Location:location}" -o table
```

All should show the same location (e.g., `eastus2`).

---

### Cost Concerns

**Monitor costs:**
```bash
# View cost analysis (requires billing reader role)
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

**Reduce costs:**
1. **Scale down Container App:**
   ```bash
   az containerapp update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --min-replicas 0 \
     --max-replicas 1
   ```

2. **Use lower SKU tiers** (for dev/test):
   - AI Services: S0 → F0 (free tier, limited)
   - Speech: S0 → F0 (free tier, limited)

---

## Deployment Checklist

Use this checklist for future deployments:

- [ ] **Prerequisites Installed**
  - [ ] Azure CLI (`az`)
  - [ ] Azure Developer CLI (`azd`)
  - [ ] Git
  - [ ] Logged in (`az login` and `azd auth login`)

- [ ] **Step 1: Azure Resources Created (BEFORE azd up)**
  - [ ] Resource Group created
  - [ ] Azure AI Foundry (Cognitive Services) created
  - [ ] GPT-4o model deployed in AI Foundry
  - [ ] Speech Service created
  - [ ] (Optional) Bing resource created
  - [ ] All resources in same region

- [ ] **Step 2: Azure AI Agent Configured**
  - [ ] Agent created in AI Foundry portal
  - [ ] NBK instructions added
  - [ ] Agent ID copied

- [ ] **Step 3: Environment Variables Set**
  - [ ] Repository cloned
  - [ ] `azd init` completed
  - [ ] All 15+ `azd env set` commands run
  - [ ] `azd env get-values` verified

- [ ] **Step 4: Container App Deployed**
  - [ ] `azd up` completed successfully
  - [ ] Container App created
  - [ ] Application URL obtained

- [ ] **Step 5: Manual Configuration**
  - [ ] API keys retrieved
  - [ ] Container App secrets set
  - [ ] All 27 environment variables configured
  - [ ] New revision created and healthy

- [ ] **Verification**
  - [ ] `/api/config` endpoint returns correct values
  - [ ] Avatar loads in browser
  - [ ] Voice recognition works (Arabic & English)
  - [ ] Agent responds correctly
  - [ ] No errors in logs

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Cloud                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Azure Container App (voicelab)                 │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  Frontend: React + TypeScript + Vite           │  │  │
│  │  │  Backend: Python Flask + WebSocket             │  │  │
│  │  │  Container: Multi-stage Docker build           │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │         Listens on: https://<app>.azurecontainerapps │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ API Calls                       │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     Azure AI Foundry (AIServices)                    │  │
│  │  - GPT-4o Deployment (chat completions)             │  │
│  │  - Azure OpenAI API                                  │  │
│  │  - Agent Framework (asst_xxx)                        │  │
│  │  Endpoint: https://<foundry>.openai.azure.com/       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ Speech API                      │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Azure Speech Service                           │  │
│  │  - Speech-to-Text (ar-SA, en-US)                    │  │
│  │  - Text-to-Speech (Andrew Multilingual)             │  │
│  │  - Avatar Synthesis (jeff, business style)          │  │
│  │  Region: eastus2 (or your selected region)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ Search API (Optional)           │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Bing Custom Search (optional)                  │  │
│  │  - Web grounding for NBK info                        │  │
│  │  - Configured for nbk.com domain                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Supporting Infrastructure                      │  │
│  │  - Container Registry (ACR) - stores Docker images  │  │
│  │  - Application Insights - monitoring & logs          │  │
│  │  - Log Analytics - log aggregation                   │  │
│  │  - Container App Environment - networking            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps After Deployment

### 1. Configure Bing Custom Search (If Using)

1. Go to [Bing Custom Search Portal](https://www.customsearch.ai/)
2. Create new instance
3. Add trusted domains:
   - `nbk.com`
   - `www.nbk.com`
4. Get Custom Configuration ID
5. Add to agent tools in AI Foundry portal

### 2. Set Up Monitoring

```bash
# Enable Application Insights alerts
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group $RESOURCE_GROUP \
  --scopes $(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --condition "count requests/failed > 10" \
  --window-size 5m
```

### 3. Configure Custom Domain (Optional)

1. Purchase domain or use existing
2. Add CNAME record pointing to Container App URL
3. Configure custom domain in Container App:
   ```bash
   az containerapp hostname add \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --hostname yourdomain.com
   ```

### 4. Set Up CI/CD (Optional)

Create GitHub Actions workflow for automated deployments:

```yaml
# .github/workflows/azure-deploy.yml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Deploy
        run: azd deploy
```

---

## Additional Resources

- **Azure Documentation:**
  - [Container Apps](https://learn.microsoft.com/azure/container-apps/)
  - [Azure AI Services](https://learn.microsoft.com/azure/ai-services/)
  - [Speech Service](https://learn.microsoft.com/azure/cognitive-services/speech-service/)
  - [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

- **Project Documentation:**
  - [Main README](./README.md) - Quick start and overview
  - [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Quick reference for common issues
  - [LOCAL-DEVELOPMENT.md](./LOCAL-DEVELOPMENT.md) - Running locally

- **Community:**
  - [Azure Container Apps GitHub](https://github.com/microsoft/azure-container-apps)
  - [Azure AI Foundry Documentation](https://ai.azure.com/docs)

---

## Summary: Key Differences from Other Guides

This guide is specifically tailored for **fresh Azure subscription deployments** and includes:

1. **✅ Explicit prerequisite creation:** Steps 1-2 MUST be completed BEFORE `azd up`
2. **✅ Clear separation:** What `azd up` does vs. what you must do manually
3. **✅ Complete variable list:** All 27 environment variables with explanations
4. **✅ PowerShell + Bash:** Commands for both Windows and Linux/macOS
5. **✅ Verification steps:** How to confirm each step succeeded
6. **✅ Real-world timings:** Expected duration for each operation
7. **✅ Known limitations:** Explains why manual Step 5 is required

**Most Important:**
> `azd up` does NOT create AI Foundry or Speech services. You must create them manually first (Steps 1-2), then run `azd up` (Step 4), then manually configure the Container App (Step 5).
