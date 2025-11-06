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
- ✅ Azure Speech Services (Arabic voice ready)
- ✅ Container Registry
- ✅ Container App
- ✅ All environment variables set
- ✅ Application running at the provided URL

**No manual environment variable setup needed!**

---

## Optional: Add AI Foundry Project & Agent (Advanced)

**Only do this if you want to use Azure AI Agents instead of direct OpenAI calls.**

By default, the app uses direct OpenAI API calls (`USE_AZURE_AI_AGENTS=false`). This works fine.

If you want to use AI Foundry Agents:

### 1. Create AI Foundry Project (Portal)
1. Go to [AI Foundry Portal](https://ai.azure.com)
2. Create a new project in your AI Services resource
3. Note the Project Name

### 2. Create an Agent (Portal)
1. In your AI Foundry project, go to **Agents**
2. Create a new agent
3. Copy the Agent ID (starts with `asst_`)

### 3. Set Environment Variables

**PowerShell:**
```powershell
azd env set AI_FOUNDRY_PROJECT_NAME "your-project-name"
azd env set AGENT_ID "asst_xxxxxxxxxxxxx"
azd env set USE_AZURE_AI_AGENTS "true"
azd deploy
```

**Bash:**
```bash
azd env set AI_FOUNDRY_PROJECT_NAME "your-project-name"
azd env set AGENT_ID "asst_xxxxxxxxxxxxx"
azd env set USE_AZURE_AI_AGENTS "true"
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
| Arabic Voice | ✅ Yes | ✅ Yes |
| Bilingual Support | ✅ Yes | ✅ Yes |
| Avatar Character | ✅ Yes | ✅ Yes |
| **AI Foundry Project** | ❌ No | ❌ Manual (optional) |
| **Agent ID** | ❌ No | ❌ Manual (optional) |
| **Bing Grounding** | ❌ No | ❌ Manual (optional) |

---

## Summary: What You Need to Set Manually

**For basic deployment (recommended):**
- **Nothing!** Just run `azd up`

**For AI Foundry Agents (optional):**
- `AI_FOUNDRY_PROJECT_NAME`
- `AGENT_ID`
- `USE_AZURE_AI_AGENTS=true`

**For Bing Grounding (optional):**
- `BING_GROUNDING_RESOURCE_NAME`
- `BING_GROUNDING_RESOURCE_KEY`

**Everything else is automatic!**

---

**Everything else is automatic!**

---

## Optional: Customize Voice/Language (Advanced)

### Change to English Voice

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
azd env set AZURE_AVATAR_CHARACTER "jeff"
azd env set AZURE_AVATAR_STYLE "business"
azd deploy
```

**Bash:**
```bash
azd env set AZURE_AVATAR_CHARACTER "jeff"
azd env set AZURE_AVATAR_STYLE "business"
azd deploy
```

Available: `lisa`, `jeff`, `anna`, `ryan` | Styles: `casual-sitting`, `business`, `technical-sitting`

---

## Testing

Open the application URL from `azd up` output and click the microphone.

**Arabic:** "مرحبا، أريد معلومات عن البنك الوطني"
**English:** "Hello, tell me about NBK services"

---

## Troubleshooting

### Verify Resources Were Created

**PowerShell:**
```powershell
$RG = azd env get-value AZURE_RESOURCE_GROUP_NAME
az cognitiveservices account list --resource-group $RG -o table
```

**Bash:**
```bash
RG=$(azd env get-value AZURE_RESOURCE_GROUP_NAME)
az cognitiveservices account list --resource-group $RG -o table
```

Should show:
- ✅ AIServices (Succeeded)
- ✅ SpeechServices (Succeeded)

### View Logs

```bash
azd logs
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

**That's it! No manual environment setup unless you want AI Foundry Agents or Bing Grounding.**
