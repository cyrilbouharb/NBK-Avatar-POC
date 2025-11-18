# Azure AI Foundry Agent Deployment Guide

This guide documents the complete process for deploying the Voice Lab application with Azure AI Foundry agents to Azure Container Apps.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and configured
- Azure Developer CLI (azd) installed
- Docker installed (for local testing)
- An Azure AI Foundry project with a pre-created agent

## Step 1: Create Your Azure AI Foundry Agent

1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Create or select your project
3. Navigate to the Agents section
4. Create a new agent and configure it with your desired:
   - Instructions/system prompt
   - Tools and capabilities
   - Model settings
5. **Save the Agent ID** (e.g., `asst_TywpnXKRSa2jEpSVvTYXpDil`)
6. **Note your Project Name** from the project URL or settings

## Step 2: Gather Required Information

Before deploying, collect the following information:

### From Azure AI Foundry Portal:
- **Agent ID**: `asst_TywpnXKRSa2jEpSVvTYXpDil` (example)
- **Project Name**: The name portion of your project endpoint
  - If endpoint is: `https://aifoundry-voicelab-twap6o64c76qm.services.ai.azure.com/api/projects/aifoundry-voicelab-twap-project`
  - Project name is: `aifoundry-voicelab-twap-project` (the last part after `/projects/`)
- **Project Endpoint**: Full URL to your AI Foundry project
- **Resource Name**: The subdomain before `.services.ai.azure.com`
- **API Key**: From your AI Foundry project settings

### Verify Project Name Match:
**CRITICAL**: The project name must match exactly between:
1. The `PROJECT_ENDPOINT` URL (last segment after `/projects/`)
2. The `AZURE_AI_PROJECT_NAME` environment variable

Example:
```
PROJECT_ENDPOINT: https://aifoundry-voicelab-twap6o64c76qm.services.ai.azure.com/api/projects/aifoundry-voicelab-twap-project
AZURE_AI_PROJECT_NAME: aifoundry-voicelab-twap-project  ✓ MUST MATCH
```

## Step 3: Configure Environment Variables

### Option A: Using .azure/{env-name}/.env file (Recommended)

Create or edit `.azure/{env-name}/.env` file:

```bash
# Azure AI Foundry Configuration
AGENT_ID=asst_TywpnXKRSa2jEpSVvTYXpDil
AI_FOUNDRY_PROJECT_NAME=aifoundry-voicelab-twap-project
```

### Option B: Set via Azure CLI (After Initial Deployment)

```bash
az containerapp update \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --set-env-vars \
    "AGENT_ID=asst_TywpnXKRSa2jEpSVvTYXpDil" \
    "AZURE_AI_PROJECT_NAME=aifoundry-voicelab-twap-project" \
    "USE_AZURE_AI_AGENTS=true"
```

## Step 4: Update Infrastructure Parameters

Edit `infra/main.parameters.json`:

```json
{
  "parameters": {
    "useFoundryAgents": {
      "value": true
    },
    "agentId": {
      "value": "${AGENT_ID=}"
    },
    "aiFoundryProjectName": {
      "value": "${AI_FOUNDRY_PROJECT_NAME=}"
    }
  }
}
```

## Step 5: (Optional) Hardcode Values in config.py for Testing

For local testing or if environment variables aren't being picked up, you can temporarily hardcode values:

Edit `backend/src/config.py`:

```python
result: Dict[str, Any] = {
    # Azure AI Foundry project configuration
    "azure_ai_resource_name": os.getenv("AZURE_AI_RESOURCE_NAME", ""),
    "azure_ai_region": os.getenv("AZURE_AI_REGION", DEFAULT_REGION),
    "azure_ai_project_name": os.getenv("AZURE_AI_PROJECT_NAME", "aifoundry-voicelab-twap-project"),  # Hardcoded fallback
    "project_endpoint": os.getenv("PROJECT_ENDPOINT", "https://aifoundry-voicelab-twap6o64c76qm.services.ai.azure.com/api/projects/aifoundry-voicelab-twap-project"),
    
    # Azure AI Agents configuration
    "use_azure_ai_agents": self._parse_bool_env("USE_AZURE_AI_AGENTS", default=True),  # Set default to True
    "agent_id": os.getenv("AGENT_ID", "asst_TywpnXKRSa2jEpSVvTYXpDil"),  # Hardcoded fallback
    # ... rest of config
}
```

**Note**: Remove hardcoded values before committing to production!

## Step 6: Deploy to Azure

### Initial Deployment

```bash
# Navigate to project directory
cd voicelive-api-salescoach

# Deploy infrastructure and application
azd deploy
```

### Verify Deployment

After deployment completes:

1. **Check environment variables are set correctly:**

```bash
az containerapp show \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --query "properties.template.containers[0].env" \
  -o table
```

Verify these values are present:
- `AGENT_ID`: Your agent ID
- `AZURE_AI_PROJECT_NAME`: Your project name (matching the endpoint)
- `USE_AZURE_AI_AGENTS`: true

2. **Check the logs:**

```bash
az containerapp logs show \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --tail 50
```

Look for:
- `Using pre-configured Azure AI Foundry agent: asst_...`
- `Connecting to Azure URL: wss://...`
- No errors about "Missing required agent connection string or project name"

## Step 7: Test the WebSocket Connection

```bash
# Install wscat if not already installed
npm install -g wscat

# Test the WebSocket endpoint
wscat -c "wss://voicelab.{your-app-domain}.azurecontainerapps.io/ws/voice"
```

Expected output:
```
Connected (press CTRL+C to quit)
< {"type": "proxy.connected", "message": "Connected to Azure Voice API"}
```

If you see an error like:
```
< {"type":"error","error":{"message":"Missing required agent connection string or project name"}}
```

This means the `AZURE_AI_PROJECT_NAME` doesn't match the project name in your `PROJECT_ENDPOINT`.

## Step 8: Troubleshooting

### Error: "Missing required agent connection string or project name"

**Root Cause**: The `project-id` parameter in the WebSocket URL doesn't match what Azure expects.

**Solution**:
1. Verify `AZURE_AI_PROJECT_NAME` matches the last segment of `PROJECT_ENDPOINT`:
   ```bash
   az containerapp show \
     --name voicelab \
     --resource-group rg-nbk-voice-test6 \
     --query "properties.template.containers[0].env[?name=='AZURE_AI_PROJECT_NAME' || name=='PROJECT_ENDPOINT']" \
     -o table
   ```

2. Update the project name if it doesn't match:
   ```bash
   az containerapp update \
     --name voicelab \
     --resource-group rg-nbk-voice-test6 \
     --set-env-vars "AZURE_AI_PROJECT_NAME=aifoundry-voicelab-twap-project"
   ```

### Error: Agent ID not being used

**Root Cause**: `USE_AZURE_AI_AGENTS` is not set to `true`, or `AGENT_ID` is empty.

**Solution**:
```bash
az containerapp update \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --set-env-vars \
    "USE_AZURE_AI_AGENTS=true" \
    "AGENT_ID=asst_TywpnXKRSa2jEpSVvTYXpDil"
```

### Viewing Debug Logs

To see the actual URL being constructed (if logging was added):

```bash
az containerapp logs show \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --tail 100 \
  --follow
```

Look for: `Connecting to Azure URL: wss://...`

The URL should contain:
- `&agent-id={your-agent-id}`
- `&project-id={your-project-name}`

## Step 9: Update Configuration Without Full Redeployment

To update only environment variables without rebuilding the container:

```bash
# Update specific environment variables
az containerapp update \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --set-env-vars \
    "AGENT_ID=new-agent-id" \
    "AZURE_AI_PROJECT_NAME=new-project-name"

# Restart the app to pick up changes
az containerapp revision restart \
  --name voicelab \
  --resource-group rg-nbk-voice-test6 \
  --revision $(az containerapp revision list \
    --name voicelab \
    --resource-group rg-nbk-voice-test6 \
    --query "[0].name" -o tsv)
```

## Key Implementation Details

### WebSocket URL Construction

The application constructs the Azure Voice API WebSocket URL as follows:

```python
# For Azure AI Foundry agents:
base_url = f"wss://{resource_name}.services.ai.azure.com/voice-live/realtime?api-version=2025-10-01&x-ms-client-request-id={uuid}"

# Adding agent and project parameters:
url = f"{base_url}&agent-id={agent_id}&project-id={project_name}"
```

### Authentication

Uses API key authentication via headers:
```python
headers = {"api-key": api_key}
```

### Configuration Priority

The application follows this priority for configuration:

1. Environment variables (highest priority)
2. Hardcoded defaults in `config.py` (fallback)
3. Empty strings (if nothing is set)

## Summary Checklist

Before deploying, ensure:

- [ ] Azure AI Foundry agent is created and you have the Agent ID
- [ ] Project name matches between `PROJECT_ENDPOINT` and `AZURE_AI_PROJECT_NAME`
- [ ] `AGENT_ID` environment variable is set
- [ ] `USE_AZURE_AI_AGENTS` is set to `true`
- [ ] `AZURE_AI_PROJECT_NAME` is set correctly
- [ ] API key is configured as a secret
- [ ] Infrastructure parameters are updated
- [ ] Code changes are committed and pushed

After deployment:

- [ ] Environment variables verified in Azure
- [ ] Logs show successful agent connection
- [ ] WebSocket test succeeds without errors
- [ ] No "Missing required agent connection string" errors

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure Voice API Documentation](https://learn.microsoft.com/azure/ai-services/openai/how-to/audio-real-time)
