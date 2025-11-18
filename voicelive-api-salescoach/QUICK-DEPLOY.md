# Quick Deployment Guide - Mobile Backend Only

## 🎯 What This Does

Deploys a **backend-only** WebSocket proxy that:
- Mobile apps connect to: `wss://your-url/ws/voice`
- Backend connects to Azure AI with your Agent ID
- No frontend included - pure API for mobile integration

---

## 📋 Prerequisites

- Azure CLI: `az login` (already logged in)
- Azure Developer CLI: `azd auth login` (already logged in)
- Git repo cloned on branch: `mobile-backend-only`

---

## 🚀 Step 1: Deploy Infrastructure

```powershell
cd voicelive-api-salescoach
azd up
```

**What it creates**:
- Azure OpenAI (GPT-4o)
- Azure Speech Services
- Container Registry
- Container App (backend)
- All networking/security

**Time**: ~15-20 minutes

**Save these values after deployment**:
```powershell
# Get your WebSocket URL
$SERVICE_URL = (azd env get-value SERVICE_VOICELAB_URI) -replace 'https://', ''
Write-Host "WebSocket: wss://$SERVICE_URL/ws/voice"
```

---

## 🤖 Step 2: Create Agent in Azure AI Foundry

### 2.1 Go to Portal

1. Open: https://ai.azure.com
2. You'll see your project (created by azd)
3. Note the **Project Name** at the top (e.g., `project-abc123`)

### 2.2 Create Agent

1. Navigate to: **Build** → **Agents** → **+ Create**
2. Fill in:
   - **Name**: `NBK Banking Customer Service`
   - **Model**: `gpt-4o` (already deployed)
   - **Instructions**:
   ```
   You are a helpful and professional NBK (National Bank of Kuwait) customer service representative.
   Keep responses SHORT and conversational (3-4 sentences max, as if speaking on phone).
   Provide accurate information about NBK banking services, products, and policies.
   Be courteous, patient, and empathetic with customers.
   Speak naturally in either Arabic or English based on customer's language preference.
   For Arabic speakers, use clear Modern Standard Arabic.
   ```
3. Click **Create**
4. **Copy the Agent ID**: `asst_xxxxxxxxxxxxxxxxxxxxx`
5. **Copy the Project Name**: from top of page

---

## ⚙️ Step 3: Configure Container App

### Get Container App Info

```powershell
$APP_NAME = azd env get-value AZURE_CONTAINER_APP_NAME
$RESOURCE_GROUP = azd env get-value AZURE_RESOURCE_GROUP
Write-Host "App: $APP_NAME"
Write-Host "Resource Group: $RESOURCE_GROUP"
```

### Set Environment Variables

**REPLACE THESE VALUES**:
- `asst_ABC123XYZ` → Your actual Agent ID (starts with `asst_`)
- `project-abc123` → Your actual Project Name from AI Foundry Portal

```powershell
# ONE LINE - Copy/paste this (replace the values first)
$AGENT_ID = "asst_ABC123XYZ"; $PROJECT_NAME = "project-abc123"; az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --set-env-vars "AGENT_ID=$AGENT_ID" "AZURE_AI_PROJECT_NAME=$PROJECT_NAME" "USE_AZURE_AI_AGENTS=true"
```

**Expected output**: `Successfully updated container app`

### Verify Configuration

```powershell
az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].env[?name=='AGENT_ID' || name=='AZURE_AI_PROJECT_NAME' || name=='USE_AZURE_AI_AGENTS'].{name:name, value:value}" --output table
```

**Should show**:
```
Name                      Value
------------------------  ------------------
AGENT_ID                  asst_ABC123XYZ
AZURE_AI_PROJECT_NAME     project-abc123
USE_AZURE_AI_AGENTS       true
```

---

## 🔄 Step 4: Redeploy Backend

After setting env vars, redeploy to apply changes:

```powershell
azd deploy
```

**Time**: ~3-5 minutes

---

## ✅ Step 5: Test Deployment

### Test Health Endpoint

```powershell
$SERVICE_URL = (azd env get-value SERVICE_VOICELAB_URI) -replace 'https://', ''
curl "https://$SERVICE_URL/api/health"
```

**Expected**:
```json
{
  "status": "healthy",
  "service": "NBK Banking Voice Backend",
  "websocket_endpoint": "/ws/voice"
}
```

### Test WebSocket Connection

**Install wscat** (if not installed):
```powershell
npm install -g wscat
```

**Connect**:
```powershell
wscat -c "wss://$SERVICE_URL/ws/voice"
```

**Expected successful output**:
```
Connected (press CTRL+C to quit)
< {"type": "proxy.connected", "message": "Connected to Azure Voice API"}
```

**If you see this ERROR**:
```json
{"type":"error","error":{"message":"Missing required agent connection string or project name"}}
```

**Solution**: 
1. Check env vars are set correctly (Step 3 verify command)
2. Make sure you redeployed after setting env vars (Step 4)
3. Wait 1-2 minutes for container to restart, then try again

---

## 📱 Step 6: Share with Mobile Team

Give them this information:

### WebSocket Endpoint
```powershell
$SERVICE_URL = (azd env get-value SERVICE_VOICELAB_URI) -replace 'https://', ''
Write-Host "`nWebSocket URL for Mobile App:"
Write-Host "wss://$SERVICE_URL/ws/voice"
```

### Audio Format Requirements
- **Format**: PCM16 (16-bit linear PCM)
- **Sample Rate**: 24000 Hz (24 kHz)
- **Channels**: Mono
- **Encoding**: Base64 for transmission

### Message Flow
```
Mobile → Backend: {"type":"input_audio_buffer.append","audio":"<base64>"}
Backend → Mobile: {"type":"proxy.connected",...}
Backend → Mobile: {"type":"response.audio.delta","delta":"<base64>",...}
```

**Full integration guide**: See `DEPLOYMENT-STEPS.md`

---

## 🐛 Troubleshooting

### Issue: WebSocket connects but immediately disconnects

**Check Container App logs**:
```powershell
az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --tail 50
```

**Common causes**:
1. ❌ `AGENT_ID` not set → Set in Step 3
2. ❌ `AZURE_AI_PROJECT_NAME` not set → Set in Step 3
3. ❌ `USE_AZURE_AI_AGENTS` not true → Set in Step 3
4. ❌ Didn't redeploy after setting vars → Run `azd deploy`

### Issue: Error "Missing required agent connection string"

**This means**: Backend is missing `AZURE_AI_PROJECT_NAME`

**Fix**:
```powershell
# Set all three env vars again
$AGENT_ID = "asst_YOUR_AGENT_ID"; $PROJECT_NAME = "your-project-name"; az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --set-env-vars "AGENT_ID=$AGENT_ID" "AZURE_AI_PROJECT_NAME=$PROJECT_NAME" "USE_AZURE_AI_AGENTS=true"

# Then redeploy
azd deploy
```

### Issue: Can't find Project Name

**Where to find it**:
1. Go to: https://ai.azure.com
2. Look at the **top center** of the page
3. Or check the URL: `https://ai.azure.com/projects/PROJECT-NAME/...`
4. Project name format: Usually `project-` followed by random characters

### Issue: Agent not responding with NBK context

**Check**:
1. Agent instructions in AI Foundry Portal
2. Agent ID matches what you configured
3. Test with simple text question first

---

## 🔄 Update Agent or Project

To change Agent ID or Project Name later:

```powershell
# Get current info
$APP_NAME = azd env get-value AZURE_CONTAINER_APP_NAME
$RESOURCE_GROUP = azd env get-value AZURE_RESOURCE_GROUP

# Update values (replace with new ones)
$AGENT_ID = "asst_NEW_AGENT_ID"; $PROJECT_NAME = "new-project-name"; az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --set-env-vars "AGENT_ID=$AGENT_ID" "AZURE_AI_PROJECT_NAME=$PROJECT_NAME"

# Redeploy
azd deploy
```

---

## 🗑️ Cleanup (Delete Everything)

```powershell
azd down --purge
```

This deletes:
- All Azure resources
- Resource group
- Container images

**Cost**: Stops all charges immediately

---

## 📊 How the Backend Works

### Architecture
```
Mobile App
    ↓ wss://your-url/ws/voice
Container App (Backend Proxy)
    ↓ wss://ai.azure.com (with agent-id & project-id)
Azure AI Foundry Agent
    ↓
Azure OpenAI + Speech Services
```

### Key Backend Logic

1. **WebSocket Handler** (`websocket_handler.py`):
   - Listens on `/ws/voice`
   - Auto-initializes NBK banking scenario
   - Connects to Azure with `AGENT_ID` and `AZURE_AI_PROJECT_NAME`
   - Proxies all messages bidirectionally

2. **URL Construction**:
   ```python
   # When USE_AZURE_AI_AGENTS=true:
   wss://{resource}.services.ai.azure.com/voice-live/realtime
     ?api-version=2025-10-01
     &agent-id={AGENT_ID}
     &project-id={AZURE_AI_PROJECT_NAME}  # ← THIS IS REQUIRED!
   ```

3. **Environment Variables Required**:
   - `AGENT_ID`: Your agent from AI Foundry Portal
   - `AZURE_AI_PROJECT_NAME`: Your project name from AI Foundry Portal
   - `USE_AZURE_AI_AGENTS`: Must be `true`
   - `AZURE_AI_RESOURCE_NAME`: Set by azd (your AI resource name)
   - `AZURE_OPENAI_API_KEY`: Set by azd (authentication)

4. **Auto-initialization**:
   - If no `AGENT_ID` env var → Creates temporary agent with NBK scenario
   - If `AGENT_ID` set → Uses your configured agent
   - Mobile app doesn't need to send initial config

---

## ✅ Success Checklist

- [ ] Deployed with `azd up`
- [ ] Created agent in AI Foundry Portal
- [ ] Copied Agent ID and Project Name
- [ ] Set env vars with `az containerapp update`
- [ ] Redeployed with `azd deploy`
- [ ] Tested health endpoint (returns `healthy`)
- [ ] Tested wscat connection (receives `proxy.connected`)
- [ ] Shared WebSocket URL with mobile team

---

## 📞 Next Steps

1. Mobile team integrates using `DEPLOYMENT-STEPS.md`
2. Test with real audio from mobile app
3. Monitor logs in Azure Portal
4. Scale if needed (Container Apps auto-scale)

**Your backend is now ready for mobile integration!** 🚀
