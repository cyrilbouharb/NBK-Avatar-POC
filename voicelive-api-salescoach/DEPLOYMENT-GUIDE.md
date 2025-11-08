# NBK Banking Avatar - Quick Deployment Guide

## Deploy Everything Automatically

```bash
cd voicelive-api-salescoach
azd auth login
azd up
```

**That's it! Everything is deployed and configured automatically:**
- ✅ Resource Group
- ✅ Azure AI Services (GPT-4o models deployed)
- ✅ Azure Speech Services (English voice ready)
- ✅ Container Registry
- ✅ Container App
- ✅ All environment variables set
- ✅ Application running at the provided URL

**No manual environment variable setup needed!**

---

## Required: Create Agent and Set Agent ID

### 1. Create Agent in Azure AI Foundry Portal

1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Select your AI Services resource (created by `azd up`)
3. Go to **Agents** → **Create Agent**
4. Configure the agent with these instructions:

```
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

5. **Copy the Agent ID** (format: `asst_xxxxxxxxxxxxxxxxxxxxx`)

### 2. Update Container App with Agent ID and Enable Agent Mode

**IMPORTANT:** You must set both `AGENT_ID` and `USE_AZURE_AI_AGENTS=true` to use your pre-configured agent.

**PowerShell:**
```powershell
$APP_NAME = azd env get-value AZURE_CONTAINER_APP_NAME
$RESOURCE_GROUP = "rg-$(azd env get-value AZURE_ENV_NAME)"
$AGENT_ID = "asst_xxxxxxxxxxxxx"  # Replace with your actual Agent ID

az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --set-env-vars "AGENT_ID=$AGENT_ID" "USE_AZURE_AI_AGENTS=true"
```

**Bash:**
```bash
APP_NAME=$(azd env get-value AZURE_CONTAINER_APP_NAME)
RESOURCE_GROUP="rg-$(azd env get-value AZURE_ENV_NAME)"
AGENT_ID="asst_xxxxxxxxxxxxx"  # Replace with your actual Agent ID

az containerapp update --name $APP_NAME --resource-group $RESOURCE_GROUP --set-env-vars "AGENT_ID=$AGENT_ID" "USE_AZURE_AI_AGENTS=true"
```

**What this does:**
- `USE_AZURE_AI_AGENTS=true` tells the application to use your Azure AI Foundry agent
- `AGENT_ID` specifies which agent to use
- Without these, the app creates temporary local agents without Bing grounding

---

## Optional: Add AI Foundry Project (Advanced)

**Only do this if you created a custom AI Foundry project.**

By default, the app uses the auto-created AI Services resource.

### Set AI Foundry Project Name

**PowerShell:**
```powershell
azd env set AI_FOUNDRY_PROJECT_NAME "your-project-name"
azd deploy
```

**Bash:**
```bash
azd env set AI_FOUNDRY_PROJECT_NAME "your-project-name"
azd deploy
```

---

## Optional: Add Bing Grounding for NBK Website

**Only do this if you want the avatar to reference NBK website content.**

### 1. Create Bing Resource (Portal)
1. Azure Portal → Create Resource → Search "Bing"
2. Create Bing Custom Search or Bing Grounding resource
3. Note the resource name and get the API key

### 2. Set Environment Variables

**PowerShell:**
```powershell
azd env set BING_GROUNDING_RESOURCE_NAME "your-bing-resource-name"
azd env set BING_GROUNDING_RESOURCE_KEY "your-bing-api-key"
azd deploy
```

**Bash:**
```bash
azd env set BING_GROUNDING_RESOURCE_NAME "your-bing-resource-name"
azd env set BING_GROUNDING_RESOURCE_KEY "your-bing-api-key"
azd deploy
```

---

## What Gets Auto-Configured by `azd up`

| Resource/Setting | Auto-Created? | Auto-Configured? |
|------------------|---------------|------------------|
| Resource Group | ✅ Yes | ✅ Yes |
| Azure AI Services | ✅ Yes | ✅ Yes |
| GPT-4o Deployment | ✅ Yes | ✅ Yes |
| Speech Services | ✅ Yes | ✅ Yes |
| Container Registry | ✅ Yes | ✅ Yes |
| Container App | ✅ Yes | ✅ Yes |
| All API Keys | ✅ Yes | ✅ Yes |
| English Voice (Andrew) | ✅ Yes | ✅ Yes |
| Bilingual Support | ✅ Yes | ✅ Yes |
| Avatar Character | ✅ Yes | ✅ Yes |
| **Agent ID** | ❌ No | ⚠️ Manual update required |
| **USE_AZURE_AI_AGENTS** | ❌ No | ⚠️ Must set to `true` to use your agent |
| **AI Foundry Project** | ❌ No | ❌ Manual (optional) |
| **Bing Grounding** | ❌ No | ❌ Manual (optional) |

---

## Summary: What You Need to Set Manually

**Required after first deployment:**
- `AGENT_ID` - Update container app with `az containerapp update`
- `USE_AZURE_AI_AGENTS=true` - **CRITICAL**: Must be set to use your Azure AI agent with Bing grounding

**Optional for AI Foundry:**
- `AI_FOUNDRY_PROJECT_NAME` (if using custom project)

**Optional for Bing Grounding:**
- `BING_GROUNDING_RESOURCE_NAME`
- `BING_GROUNDING_RESOURCE_KEY`

**Everything else is automatic!**

---

## Optional: Customize Voice/Language (Advanced)

### Change Voice

**PowerShell:**
```powershell
azd env set AZURE_VOICE_NAME "en-US-AvaMultilingualNeural"
azd deploy
```

**Bash:**
```bash
azd env set AZURE_VOICE_NAME "en-US-AvaMultilingualNeural"
azd deploy
```

### Change Avatar Character

**PowerShell:**
```powershell
azd env set AZURE_AVATAR_CHARACTER "lisa"
azd env set AZURE_AVATAR_STYLE "casual-sitting"
azd deploy
```

**Bash:**
```bash
azd env set AZURE_AVATAR_CHARACTER "lisa"
azd env set AZURE_AVATAR_STYLE "casual-sitting"
azd deploy
```

---

## Testing

Open the application URL from `azd up` output and click the microphone.

**English:** "Hello, tell me about NBK services"
**Arabic:** "مرحبا، أريد معلومات عن البنك الوطني"

---

## Troubleshooting

### Verify Resources Were Created

**PowerShell:**
```powershell
$APP_NAME = azd env get-value AZURE_CONTAINER_APP_NAME
$RG = "rg-$(azd env get-value AZURE_ENV_NAME)"
az cognitiveservices account list --resource-group $RG -o table
```

**Bash:**
```bash
APP_NAME=$(azd env get-value AZURE_CONTAINER_APP_NAME)
RG="rg-$(azd env get-value AZURE_ENV_NAME)"
az cognitiveservices account list --resource-group $RG -o table
```

Should show:
- ✅ AIServices (Succeeded)
- ✅ SpeechServices (Succeeded)

### View Logs

```bash
azd logs
```

Or:

```powershell
az containerapp logs show --name $APP_NAME --resource-group $RG --tail 100
```

### Redeploy

```bash
azd deploy
```

---

## Clean Up

```bash
azd down
```

---

**That's it! Start training with your avatar!**

---

## Clean Up

```bash
azd down
```

---

**That's it! No manual environment setup unless you want AI Foundry Agents or Bing Grounding.**
