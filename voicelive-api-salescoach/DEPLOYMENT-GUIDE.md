# NBK Banking Avatar - Deployment and Configuration Guide

## Overview

This guide walks you through deploying and configuring the NBK Banking Customer Service Avatar with bilingual support (Arabic/English) and Bing Custom Search grounding on NBK website content.

## Prerequisites

- Azure subscription
- Azure Developer CLI (`azd`) installed
- Docker Desktop (for local development)
- VS Code (recommended)

## Architecture

The solution uses:
- **Azure AI Foundry** - GPT-4o model for conversation
- **Azure Speech Services** - Arabic (`ar-SA-ZariyahNeural`) and English voice
- **Azure Voice Live API** - Real-time voice streaming
- **Bing Grounding with Custom Search** - NBK website content grounding
- **Azure Container Apps** - Hosting the containerized application

## Deployment Steps

### 1. Initial Deployment

```bash
# Clone the repository
git clone <your-repo-url>
cd voicelive-api-salescoach

# Login to Azure
azd auth login

# Deploy infrastructure and application
azd up
```

This will:
- Create all Azure resources (AI Foundry, Speech, Container Apps, etc.)
- Build and deploy the containerized application
- Output the application URL

### 2. Configure Bing Custom Search for NBK Website

After deployment, you need to configure Bing Custom Search to ground the agent on NBK website content:

#### Step 2.1: Access Bing Grounding Resource

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group (e.g., `rg-nbk-avatar`)
3. Find the Bing Grounding resource (name starts with `bing-grounding-`)

#### Step 2.2: Create Configuration Instance

1. In the Bing Grounding resource, go to **Resource Management** → **Configurations**
2. Click **Create a new configuration**
3. Enter configuration details:

**Name**: `NBK-Website-Search`

**Allowed Domains** (add these URLs):
```
https://www.nbk.com/kuwait
https://www.nbk.com/kuwait/personal/cards/credit-cards.html
https://www.nbk.com/kuwait/investments/nbk-invest-app/guided-investments.html
```

**Include Subpages**: Yes (to index all pages under these domains)

**Note**: Start with these specific NBK Kuwait domains. You can add more domains later as needed.

**Market**: `en-US` (for English) and `ar-SA` (for Arabic)

4. Click **Save** and note the **Configuration ID** (you'll need this next)

#### Step 2.3: Update Application Configuration

```bash
# Set the Bing configuration ID
azd env set BING_GROUNDING_CONFIG_ID <your-configuration-id>

# Redeploy to apply changes
azd up
```

### 3. Configure Agent in AI Foundry Portal

1. Go to [Azure AI Foundry Portal](https://ai.azure.com)
2. Navigate to your project
3. Go to **Agents** section
4. Find your agent (or it will be created on first use)
5. In the **Setup** pane, scroll to **Knowledge**
6. Click **Add** → Select **Grounding with Bing Custom Search**
7. Select your Bing Grounding resource
8. Select the configuration: `NBK-Website-Search`
9. Click **Save**

## Language Configuration

### Arabic Voice (Default)

The application is configured to use Arabic by default with a voice suitable for Kuwaiti customers:

- **Voice**: `ar-SA-ZariyahNeural` (Saudi Arabian female neural voice)
- **Language**: `ar-SA` (Modern Standard Arabic)
- **Alternative voices**:
  - `ar-SA-HamedNeural` (Male)
  - `ar-KW-FahedNeural` (Kuwaiti male - if available)

### English Voice Support

To switch to English:

```bash
azd env set VOICE_NAME en-US-AvaMultilingualNeural
azd env set SPEECH_LANGUAGE en-US
azd up
```

### Bilingual Auto-Detection

The agent automatically detects the customer's language and responds accordingly. No additional configuration needed.

## Testing the Deployment

1. Open the deployed application URL (from `azd up` output)
2. Click the microphone button
3. Test in Arabic:
   ```
   "مرحبا، أريد معلومات عن حسابات التوفير في البنك الوطني"
   (Hello, I want information about savings accounts at National Bank)
   ```
4. Test in English:
   ```
   "Hello, can you tell me about NBK credit cards?"
   ```

## Troubleshooting

### Agent not using Bing Search

**Problem**: Agent responds but doesn't cite NBK website sources

**Solution**:
1. Verify Bing configuration ID is set: `azd env get-values | grep BING`
2. Check that NBK domains are indexed by Bing (may take 24-48 hours)
3. Verify the configuration is attached to the agent in AI Foundry Portal

### Arabic Voice Not Working

**Problem**: Voice is in English or not playing

**Solution**:
1. Check environment variables:
   ```bash
   azd env get-values | grep VOICE
   azd env get-values | grep SPEECH
   ```
2. Verify Speech Services resource supports Arabic in your region
3. Try alternative Arabic voices if current one isn't available

### Missing Configuration ID

**Problem**: `BING_GROUNDING_CONFIG_ID` not set

**Solution**:
1. Go to Azure Portal → Bing Grounding resource → Configurations
2. Copy the Configuration ID
3. Set it: `azd env set BING_GROUNDING_CONFIG_ID <config-id>`
4. Redeploy: `azd up`

## Customization

### Change Agent Behavior

Edit the agent prompt in `data/scenarios/nbk-banking-role-play.prompt.yml`

### Add More NBK Domains

1. Azure Portal → Bing Grounding → Configurations → Edit
2. Add new domains under **Allowed Domains**
3. Save changes (no redeployment needed)

### Adjust Voice Settings

```bash
# Change voice
azd env set VOICE_NAME <voice-name>

# Change language
azd env set SPEECH_LANGUAGE <language-code>

# Apply changes
azd up
```

## Cost Optimization

- **Development**: Use smaller GPT model (`gpt-4o-mini`)
- **Production**: Monitor usage in Azure Portal → Cost Management
- **Bing Search**: Billed per agent tool call (check pricing page)

## Security Considerations

1. **Never ask for credentials**: The agent is configured to never request sensitive information
2. **Private endpoints**: For production, enable private endpoints in `resources.bicep`
3. **RBAC**: Use managed identities (already configured)
4. **Monitoring**: Application Insights is enabled for audit logs

## Next Steps

1. ✅ Deploy infrastructure
2. ✅ Configure Bing Custom Search
3. ✅ Test bilingual conversations
4. 📝 Customize agent prompts for specific NBK use cases
5. 📊 Monitor usage and costs
6. 🔒 Enable additional security features for production

## Support

For issues or questions:
- Check Azure Portal → Resource Group → Deployments for errors
- View logs: `azd logs`
- Application Insights for runtime errors

---

**Important Notes:**
- Bing Custom Search requires NBK website to be publicly indexed by Bing
- First deployment takes ~8-10 minutes
- Configuration changes may take a few minutes to propagate
- Test thoroughly before production use
