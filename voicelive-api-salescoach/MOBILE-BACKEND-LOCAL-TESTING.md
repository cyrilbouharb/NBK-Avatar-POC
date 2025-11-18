# Testing Mobile Backend Locally

## 🎯 Overview

This guide shows how to test the **mobile-backend-only** branch locally without deploying to Azure.

---

## 📋 Prerequisites

- Python 3.11+
- Azure OpenAI resource (deployed)
- Azure Speech Services resource (deployed)
- Azure AI Foundry agent (optional for testing)

---

## ⚙️ Step 1: Create Environment File

Create `backend\.env` with your Azure credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
MODEL_DEPLOYMENT_NAME=gpt-4o

# Azure Speech Services
AZURE_SPEECH_KEY=your-speech-key
AZURE_SPEECH_REGION=eastus

# Voice Configuration
AZURE_VOICE_NAME=ar-SA-ZariyahNeural
AZURE_SPEECH_LANGUAGE=ar-SA,en-US

# Optional: Azure AI Foundry Agent
AGENT_ID=asst_xxxxxxxxxxxxx
USE_AZURE_AI_AGENTS=true

# Optional: AI Services (if using Azure AI Foundry)
AZURE_AI_RESOURCE_NAME=your-ai-resource-name

# Server Configuration
PORT=8000
```

**How to get these values**:

### If you've already deployed with `azd`:
```powershell
# Get all environment values
azd env get-values

# Copy the relevant values to backend\.env
```

### If you haven't deployed yet:
1. Go to [Azure Portal](https://portal.azure.com)
2. Find your Azure OpenAI resource → **Keys and Endpoint**
3. Find your Speech Services resource → **Keys and Endpoint**
4. Copy the values

---

## 🚀 Step 2: Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

## ▶️ Step 3: Start Backend Server

```powershell
cd backend
python -m src.app
```

You should see:
```
 * Running on http://127.0.0.1:8000
 * Running on all addresses (0.0.0.0)
```

**Note**: The backend will auto-initialize with the NBK Banking scenario on WebSocket connection.

---

## ✅ Step 4: Test the Endpoints

### Test Health Endpoint

```powershell
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "NBK Banking Voice Backend",
  "websocket_endpoint": "/ws/voice"
}
```

### Test Config Endpoint

```powershell
curl http://localhost:8000/api/config
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

### Test WebSocket Connection

Install `wscat` (if not already installed):
```powershell
npm install -g wscat
```

Connect to WebSocket:
```powershell
wscat -c ws://localhost:8000/ws/voice
```

You should receive:
```json
{"type":"proxy.connected","message":"Connected to Azure Voice API"}
```

---

## 🎤 Step 5: Test with Audio

### Option A: Use wscat with Manual Messages

1. Connect to WebSocket:
```powershell
wscat -c ws://localhost:8000/ws/voice
```

2. Send audio configuration:
```json
{
  "type": "session.update",
  "session": {
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16"
  }
}
```

3. Send base64-encoded audio (PCM16 24kHz mono):
```json
{
  "type": "input_audio_buffer.append",
  "audio": "<base64-encoded-pcm16-audio>"
}
```

### Option B: Use Python Test Script

Create `test_websocket.py`:

```python
import asyncio
import websockets
import json
import base64

async def test_voice_connection():
    uri = "ws://localhost:8000/ws/voice"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection message
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # Configure session
        config = {
            "type": "session.update",
            "session": {
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16"
            }
        }
        await websocket.send(json.dumps(config))
        
        # Wait for responses
        try:
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received: {data['type']}")
                
                # Print transcript if available
                if data['type'] == 'conversation.item.input_audio_transcription.completed':
                    print(f"User said: {data.get('transcript', '')}")
                elif data['type'] == 'response.audio_transcript.done':
                    print(f"Agent said: {data.get('transcript', '')}")
                    
        except KeyboardInterrupt:
            print("\nDisconnecting...")

if __name__ == "__main__":
    asyncio.run(test_voice_connection())
```

Run it:
```powershell
python test_websocket.py
```

### Option C: Use Mobile App Simulators

Test with actual iOS/Android code from `MOBILE-INTEGRATION-GUIDE.md`:
- Change WebSocket URL to `ws://localhost:8000/ws/voice`
- Use local network IP if testing on physical device

---

## 🧪 Test Scenarios

### Scenario 1: Auto-Initialization (No AGENT_ID)

Remove `AGENT_ID` from `backend\.env`:
```env
# AGENT_ID=  # Commented out
USE_AZURE_AI_AGENTS=false
```

**Expected**: Backend auto-creates agent with NBK Banking scenario

**Verification**:
```
Backend logs should show:
"Auto-creating agent with default NBK Banking scenario"
```

### Scenario 2: Pre-configured Azure Agent

Set `AGENT_ID` in `backend\.env`:
```env
AGENT_ID=asst_xxxxxxxxxxxxx
USE_AZURE_AI_AGENTS=true
```

**Expected**: Backend uses your Azure AI Foundry agent

**Verification**:
```
Backend logs should show:
"Using pre-configured Azure AI Foundry agent"
```

### Scenario 3: Simulate Mobile Connection

Use the iOS/Android example code but change:
```swift
// iOS
let wsURL = URL(string: "ws://localhost:8000/ws/voice")!
// Or use your computer's IP for physical device
let wsURL = URL(string: "ws://192.168.1.100:8000/ws/voice")!
```

```kotlin
// Android
val wsUrl = "ws://localhost:8000/ws/voice"
// Or use computer's IP
val wsUrl = "ws://192.168.1.100:8000/ws/voice"
```

---

## 🐛 Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'flask'`
```powershell
cd backend
pip install -r requirements.txt
```

**Error**: `AZURE_OPENAI_ENDPOINT not set`
```
Create backend\.env file with your Azure credentials (see Step 1)
```

**Error**: `Port 8000 already in use`
```powershell
# Change port in backend\.env
PORT=8001

# Or kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process-id> /F
```

### WebSocket connection fails

**Issue**: `wscat -c ws://localhost:8000/ws/voice` hangs

**Check**:
1. Backend is running: `curl http://localhost:8000/api/health`
2. No firewall blocking: Check Windows Firewall
3. Backend logs for errors

**Issue**: Receives error message from Azure

**Check**:
1. Azure credentials in `backend\.env` are correct
2. Azure OpenAI deployment name matches `MODEL_DEPLOYMENT_NAME`
3. Speech Services key and region are correct

### No audio response

**Issue**: WebSocket connects but no audio received

**Check**:
1. Audio format is PCM16 24kHz mono
2. Audio data is base64-encoded
3. Backend logs show audio being processed
4. Azure Speech Services quota not exceeded

### Agent not responding correctly

**Issue**: Agent gives generic responses, not NBK Banking context

**Check**:
1. If using `AGENT_ID`: Verify agent instructions in Azure AI Foundry Portal
2. If auto-creating: Check `data/scenarios/nbk-banking-role-play.prompt.yml` exists
3. Backend logs for agent creation messages

---

## 📊 Monitor Local Backend

### View Console Logs

The backend prints logs to console:
```
[2025-11-18 10:30:45] INFO: WebSocket connected
[2025-11-18 10:30:45] INFO: Using pre-configured Azure AI Foundry agent: asst_xxx
[2025-11-18 10:30:46] INFO: Connected to Azure Voice API
[2025-11-18 10:30:50] INFO: Received audio from client
```

### Debug Mode

For more verbose logging, modify `backend/src/app.py`:
```python
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=True  # Add this line
    )
```

---

## 🔄 Test Changes

After modifying code:

1. Stop backend: `Ctrl+C`
2. Restart backend: `python -m src.app`
3. Test WebSocket again

**Hot reload**: Flask debug mode enables hot reload for most changes.

---

## 🌐 Test from Physical Mobile Device

If testing on a physical iOS/Android device:

1. **Find your computer's IP**:
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

2. **Ensure backend listens on all interfaces** (already configured):
```python
app.run(host="0.0.0.0", port=8000)
```

3. **Update mobile app WebSocket URL**:
```
ws://192.168.1.100:8000/ws/voice
```

4. **Allow firewall access** (Windows):
```powershell
# Add inbound rule for port 8000
New-NetFirewallRule -DisplayName "Python Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

5. **Ensure same network**: Device and computer must be on same WiFi.

---

## ✅ Verify Everything Works

Complete checklist:

- [ ] Backend starts without errors
- [ ] Health endpoint returns `healthy`
- [ ] Config endpoint returns `mobile_backend` mode
- [ ] WebSocket connection establishes successfully
- [ ] Receives `proxy.connected` message
- [ ] Can send/receive audio messages (if testing with audio)
- [ ] Agent responds with NBK Banking context
- [ ] No errors in backend console

---

## 🎉 Ready for Mobile Integration

Once local testing passes:
1. Share your computer's IP and port with mobile developers
2. They can test integration before Azure deployment
3. When ready, deploy to Azure using `MOBILE-DEPLOYMENT-GUIDE.md`

---

## 📝 Quick Reference

| Endpoint | URL | Purpose |
|----------|-----|---------|
| Health | `http://localhost:8000/api/health` | Check backend status |
| Config | `http://localhost:8000/api/config` | Get configuration |
| WebSocket | `ws://localhost:8000/ws/voice` | Voice streaming |

| Tool | Command | Purpose |
|------|---------|---------|
| curl | `curl http://localhost:8000/api/health` | Test HTTP |
| wscat | `wscat -c ws://localhost:8000/ws/voice` | Test WebSocket |
| Python | `python test_websocket.py` | Automated testing |

---

**Happy Testing! 🚀**
