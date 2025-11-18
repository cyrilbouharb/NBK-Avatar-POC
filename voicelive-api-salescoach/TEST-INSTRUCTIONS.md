# Testing Instructions

## What We Fixed

Changed `.env` configuration:
```env
USE_AZURE_AI_AGENTS=false  # Changed from true
```

**Why**: Your agent (`asst_wgsM81Hm1FuLOJemAeEfrYQr`) is hosted on Azure OpenAI Cognitive Services (`.cognitiveservices.azure.com`), not on a separate AI Foundry hub (`.services.ai.azure.com`).

## Test the Backend

### 1. Start Backend (in Terminal 1)
```powershell
cd "c:\Users\cyrilbouharb\POCs\Avatar IP\voicelive-api-salescoach\backend"
python -m src.app
```

Wait for:
```
Starting NBK Banking Voice Backend on http://0.0.0.0:8000
```

### 2. Test Health Endpoint (in Terminal 2)
```powershell
curl http://localhost:8000/api/health
```

Expected:
```json
{"status":"healthy","service":"NBK Banking Voice Backend","websocket_endpoint":"/ws/voice"}
```

### 3. Test WebSocket Connection
```powershell
wscat -c ws://localhost:8000/ws/voice
```

**What to expect**:

✅ **Success**: You'll see:
```json
{"type":"proxy.connected","message":"Connected to Azure Voice API"}
```

❌ **If it fails**: Check Terminal 1 for error logs from the backend.

## Possible Issues

### Issue: HTTP 404 from Azure

**Cause**: The Voice Chat API endpoint (`/voice-agent/realtime` with API version `2025-10-01`) might not be available on your Azure OpenAI resource yet.

**Solution**: The Voice Chat API is in very early preview. You may need to:
1. Request access to the preview
2. Or use a different Azure region that has the API enabled
3. Or wait for the API to become generally available

### Issue: HTTP 401 Unauthorized

**Cause**: API key is incorrect

**Solution**: Check your `AZURE_OPENAI_API_KEY` in `.env`

### Issue: Connection timeout

**Cause**: Network or firewall issue

**Solution**: Check your internet connection and firewall settings

## What the Backend Logs Should Show

When you connect with `wscat`, watch Terminal 1 for:

```
INFO:src.services.websocket_handler:Using pre-configured Azure AI Foundry agent: asst_wgsM81Hm1FuLOJemAeEfrYQr
INFO:src.services.websocket_handler:Connecting to Azure URL: wss://aifoundry-voicelab-6ng26fguwmnci.cognitiveservices.azure.com/voice-agent/realtime?api-version=2025-10-01&agent-id=asst_wgsM81Hm1FuLOJemAeEfrYQr
INFO:src.services.websocket_handler:Connected to Azure Voice API with agent: asst_wgsM81Hm1FuLOJemAeEfrYQr
```

**Or if it fails**:
```
ERROR:src.services.websocket_handler:Failed to connect to Azure: [error message]
```

## Next Steps

1. **If connection succeeds**: The mobile backend is working! You can proceed with mobile integration.

2. **If connection fails with 404**: The Voice Chat API may not be enabled on your resource. You have options:
   - Request preview access from Microsoft
   - Deploy to a region with the API enabled
   - Wait for general availability

3. **Alternative**: Use the old master branch which uses the standard Realtime API (without the Voice Chat preview features).

## Key Configuration Summary

Your current setup:
- **Resource**: `aifoundry-voicelab-6ng26fguwmnci.cognitiveservices.azure.com`
- **Agent ID**: `asst_wgsM81Hm1FuLOJemAeEfrYQr`
- **API Version**: `2025-10-01` (Voice Chat API preview)
- **Endpoint**: `/voice-agent/realtime`
- **Domain**: Cognitive Services (not AI Foundry hub)
