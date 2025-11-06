# NBK Banking Avatar - Quick Deployment Guide

## Prerequisites

- Azure subscription
- Azure Developer CLI (`azd`) [Install here](https://aka.ms/azd-install)

## 1. Deploy with One Command

**From the project directory:**

```bash
cd voicelive-api-salescoach
azd auth login
azd up
```

**That's it!** The deployment automatically creates:
- ✅ Azure AI Services (for GPT-4o)
- ✅ Azure Speech Services (for Avatar voice)
- ✅ Container App with your application
- ✅ All environment variables configured

## 2. (Optional) Add Bing Grounding

**Only if you want NBK website content grounding:**

### PowerShell:
```powershell
# Set your Bing API key (get from Azure Portal)
azd env set BING_GROUNDING_RESOURCE_KEY "your-bing-key-here"
azd env set BING_GROUNDING_RESOURCE_NAME "your-bing-resource-name"

# Redeploy
azd up
```

### Bash:
```bash
# Set your Bing API key (get from Azure Portal)
azd env set BING_GROUNDING_RESOURCE_KEY "your-bing-key-here"
azd env set BING_GROUNDING_RESOURCE_NAME "your-bing-resource-name"

# Redeploy
azd up
```

## 3. Access Your Application

After deployment completes, you'll see:
```
SUCCESS: Your application is running at: https://voicelab.xxxxx.azurecontainerapps.io/
```

Click the URL and start chatting with the avatar!

## Essential Environment Variables (Auto-Configured)

These are **automatically set** by `azd up` - you don't need to configure them:

| Variable | Purpose | Auto-Set? |
|----------|---------|-----------|
| `AZURE_OPENAI_ENDPOINT` | AI Services endpoint | ✅ Yes |
| `AZURE_OPENAI_API_KEY` | AI Services key | ✅ Yes |
| `AZURE_SPEECH_KEY` | Speech Services key | ✅ Yes |
| `AZURE_SPEECH_REGION` | Speech region | ✅ Yes |
| `MODEL_DEPLOYMENT_NAME` | GPT model name | ✅ Yes (gpt-4o) |
| `AZURE_VOICE_NAME` | Avatar voice | ✅ Yes (ar-SA-ZariyahNeural) |
| `AZURE_SPEECH_LANGUAGE` | Languages | ✅ Yes (ar-SA,en-US) |
| `AZURE_AVATAR_CHARACTER` | Avatar character | ✅ Yes (lisa) |
| `AZURE_AVATAR_STYLE` | Avatar style | ✅ Yes (casual-sitting) |

## Optional: Customize Voice/Language

### Change to English Voice

**PowerShell:**
```powershell
azd env set AZURE_VOICE_NAME "en-US-AvaMultilingualNeural"
azd up
```

**Bash:**
```bash
azd env set AZURE_VOICE_NAME "en-US-AvaMultilingualNeural"
azd up
```

### Change Avatar Character

**PowerShell:**
```powershell
azd env set AZURE_AVATAR_CHARACTER "jeff"
azd env set AZURE_AVATAR_STYLE "business"
azd up
```

**Bash:**
```bash
azd env set AZURE_AVATAR_CHARACTER "jeff"
azd env set AZURE_AVATAR_STYLE "business"
azd up
```

Available avatars: `lisa`, `jeff`, `anna`, `ryan`
Available styles: `casual-sitting`, `business`, `technical-sitting`

## Testing

1. Open the application URL
2. Click microphone button
3. Speak in Arabic or English
4. The avatar responds with voice and animation

**Arabic test:**
```
"مرحبا، أريد معلومات عن البنك الوطني"
```

**English test:**
```
"Hello, tell me about NBK services"
```

## Troubleshooting

### Check if resources were created

**PowerShell:**
```powershell
$RG = azd env get-value AZURE_RESOURCE_GROUP_NAME
az cognitiveservices account list --resource-group $RG --query "[].{Name:name, Kind:kind, Status:properties.provisioningState}" -o table
```

**Bash:**
```bash
RG=$(azd env get-value AZURE_RESOURCE_GROUP_NAME)
az cognitiveservices account list --resource-group $RG --query "[].{Name:name, Kind:kind, Status:properties.provisioningState}" -o table
```

You should see:
- ✅ AIServices (Status: Succeeded)
- ✅ SpeechServices (Status: Succeeded)

### View application logs

**PowerShell:**
```powershell
azd logs
```

**Bash:**
```bash
azd logs
```

### Redeploy if needed

**PowerShell/Bash:**
```bash
azd deploy
```

## Cost Estimate

- **Development/Testing:** ~$10-30/month
- **Production (moderate use):** ~$100-300/month

Costs depend on:
- GPT-4o usage (per token)
- Speech synthesis (per character)
- Avatar video streaming (per minute)

## Clean Up

**Remove all resources:**

**PowerShell/Bash:**
```bash
azd down
```

---

## That's It!

The deployment is designed to be simple:
1. Run `azd up`
2. Everything is configured automatically
3. Start using the avatar

No manual environment variable configuration needed unless you want Bing grounding or customization.

---

**Support:**
- View deployment status: [Azure Portal](https://portal.azure.com)
- Check logs: `azd logs`
- Redeploy: `azd deploy`
