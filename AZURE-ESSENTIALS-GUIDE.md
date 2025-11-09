# 🚀 Azure AI Voice Agent - Essentials Guide

**Step-by-step guide for creating and connecting to Azure AI Voice Live API using Azure AI Foundry**

---

## 📋 Table of Contents

1. [What You Need from Azure](#what-you-need-from-azure)
2. [Step 1: Create Azure AI Agent in Portal](#step-1-create-azure-ai-agent-in-portal)
3. [Step 2: Configure Your Backend](#step-2-configure-your-backend)
4. [Step 3: Connect to Azure Voice Live API](#step-3-connect-to-azure-voice-live-api)
5. [Step 4: Send Session Configuration](#step-4-send-session-configuration)
6. [Connection Flow Diagram](#connection-flow-diagram)
7. [Quick Start Checklist](#quick-start-checklist)

---

## What You Need from Azure

### **Required Azure Resources:**

| Resource | Purpose | Where to Get It |
|----------|---------|-----------------|
| **Azure OpenAI Service** | GPT-4o model for conversations | Azure Portal → Create Azure OpenAI |
| **Azure AI Foundry Hub** | Central management for AI projects | ai.azure.com → Create Hub |
| **Azure AI Foundry Project** | Contains agents and configurations | ai.azure.com → Create Project |
| **Azure Speech Services** | Speech-to-Text & Text-to-Speech | Included with Azure OpenAI |

### **Configuration Values You'll Need:**

```bash
# From Azure Portal
AZURE_AI_RESOURCE_NAME=your-resource-name          # e.g., "nbk-openai-resource"
AZURE_OPENAI_API_KEY=abc123...                     # From Keys section
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# From Azure AI Foundry Portal (ai.azure.com)
AZURE_AI_PROJECT_NAME=your-project-name            # e.g., "nbk-voice-project"

# If using Azure AI Foundry Agent (Approach 1)
AGENT_ID=asst_abc123...                            # After creating agent
```

---

## Step 1: Create Azure AI Agent in Portal

### **1.1: Access Azure AI Foundry**

1. Go to **https://ai.azure.com**
2. Sign in with your Azure account
3. Navigate to your **Project** (or create one if needed)

---

### **1.2: Create Your Agent**

1. Click **"Agents"** in the left sidebar
2. Click **"+ New Agent"** button
3. Fill in the agent details:

**Basic Information:**
```yaml
Name: NBK Banking Assistant
Description: Professional banking customer service for National Bank of Kuwait
```

**Instructions (System Prompt):**
```
You are a professional customer service representative for 
National Bank of Kuwait (NBK).

Your role:
- Assist customers with banking inquiries
- Provide accurate information about NBK services
- Communicate clearly in Arabic and English
- Keep responses brief (2-3 sentences max)
- Never ask for sensitive credentials like passwords or PINs

Remember: Be professional, helpful, and trustworthy!
```

**Model Configuration:**
```yaml
Model: gpt-4o
Temperature: 0.7
Max Tokens: 2000
```

4. Click **"Create"**

---

### **1.3: Copy Your Agent ID**

After creation, you'll see your agent details. **Copy the Agent ID** - it looks like:
```
asst_wgsM81Hm1FuLOJemAeEfrYQr
```

✅ **This is the most important value - you'll need it to connect!**

---

## Step 2: Configure Your Backend

### **2.1: Create .env File**

Create a `.env` file in your project root with these values:

```bash
# ═══════════════════════════════════════════════════════════
# Azure Resources (Get from Azure Portal)
# ═══════════════════════════════════════════════════════════
AZURE_AI_RESOURCE_NAME=your-resource-name
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_AI_PROJECT_NAME=your-project-name

# ═══════════════════════════════════════════════════════════
# Azure AI Agent Configuration
# ═══════════════════════════════════════════════════════════
USE_AZURE_AI_AGENTS=true
AGENT_ID=asst_wgsM81Hm1FuLOJemAeEfrYQr  # ← Your Agent ID from Step 1.3

# ═══════════════════════════════════════════════════════════
# Audio Settings (Optional - defaults work fine)
# ═══════════════════════════════════════════════════════════
AZURE_VOICE_NAME=en-US-AndrewMultilingualNeural
AZURE_INPUT_TRANSCRIPTION_LANGUAGE=en-US
AZURE_INPUT_TRANSCRIPTION_MODEL=azure-speech
```

### **2.2: Where to Find These Values**

| Variable | Where to Find It |
|----------|------------------|
| `AZURE_AI_RESOURCE_NAME` | Azure Portal → Your OpenAI Resource → Overview → Name |
| `AZURE_OPENAI_API_KEY` | Azure Portal → Your OpenAI Resource → Keys and Endpoint |
| `AZURE_AI_PROJECT_NAME` | Azure AI Foundry → Your Project → Settings → Name |
| `AGENT_ID` | Azure AI Foundry → Agents → Your Agent → Copy ID |

---

## Step 3: Connect to Azure Voice Live API

### **3.1: Python Code to Connect**

```python
import websockets
import json
from typing import Optional

# Load from .env
AZURE_AI_RESOURCE_NAME = "your-resource-name"
AZURE_OPENAI_API_KEY = "your-api-key"
AGENT_ID = "asst_wgsM81Hm1FuLOJemAeEfrYQr"
AZURE_AI_PROJECT_NAME = "your-project-name"


async def connect_to_azure_voice_api(agent_id: str) -> websockets.ClientConnection:
    """
    Connect to Azure Voice Live API with Azure AI Agent.
    
    This establishes the WebSocket connection to Azure.
    """
    # Build the WebSocket URL
    url = (
        f"wss://{AZURE_AI_RESOURCE_NAME}.services.ai.azure.com/"
        f"voice-live/realtime"
        f"?api-version=2025-10-01"
        f"&agent-id={agent_id}"
        f"&project-id={AZURE_AI_PROJECT_NAME}"
    )
    
    # Set authentication header
    headers = {
        "api-key": AZURE_OPENAI_API_KEY
    }
    
    # Connect to Azure
    print(f"🔗 Connecting to Azure Voice API...")
    azure_ws = await websockets.connect(url, additional_headers=headers)
    print(f"✅ Connected! Agent: {agent_id}")
    
    return azure_ws
```

### **3.2: Understanding the URL**

```
wss://your-resource.services.ai.azure.com/voice-live/realtime
    ↑               ↑                      ↑
  Protocol    Azure AI Foundry          Voice Live
              Domain                     Endpoint

?api-version=2025-10-01
    ↑
  API Version (required)

&agent-id=asst_abc123
    ↑
  Your Agent ID from Step 1.3

&project-id=your-project-name
    ↑
  Your Project Name
```

**Key Points:**
- ✅ Use `services.ai.azure.com` domain (Azure AI Foundry)
- ✅ Endpoint is `voice-live/realtime`
- ✅ Must include `agent-id` and `project-id` parameters
- ✅ Authentication via `api-key` header

---

## Step 4: Send Session Configuration

### **4.1: What Configuration to Send**

**Important:** When using Azure AI Agents, you only send **audio and voice settings**. 
The AI instructions, model, and temperature are already configured in the Azure Portal!

### **4.2: Python Code to Send Config**

```python
async def send_session_config(azure_ws: websockets.ClientConnection) -> None:
    """
    Send session configuration to Azure.
    
    For Azure AI Agents, we only send audio/voice settings.
    Instructions are already in the Azure Portal!
    """
    config_message = {
        "type": "session.update",
        "session": {
            # ═══════════════════════════════════════════════════════
            # Modalities - Enable both text and audio
            # ═══════════════════════════════════════════════════════
            "modalities": ["text", "audio"],
            
            # ═══════════════════════════════════════════════════════
            # Turn Detection - When does the user stop speaking?
            # ═══════════════════════════════════════════════════════
            "turn_detection": {
                "type": "azure_semantic_vad"  # Voice Activity Detection
            },
            
            # ═══════════════════════════════════════════════════════
            # Speech-to-Text Configuration
            # ═══════════════════════════════════════════════════════
            "input_audio_transcription": {
                "model": "azure-speech",      # Azure Speech Service
                "language": "en-US"           # Transcription language
            },
            
            # ═══════════════════════════════════════════════════════
            # Audio Preprocessing
            # ═══════════════════════════════════════════════════════
            "input_audio_noise_reduction": {
                "type": "azure_deep_noise_suppression"  # Remove background noise
            },
            
            "input_audio_echo_cancellation": {
                "type": "server_echo_cancellation"  # Prevent echo/feedback
            },
            
            # ═══════════════════════════════════════════════════════
            # Visual Avatar (if using video component)
            # ═══════════════════════════════════════════════════════
            "avatar": {
                "character": "jeff",
                "style": "business"
            },
            
            # ═══════════════════════════════════════════════════════
            # Text-to-Speech Voice
            # ═══════════════════════════════════════════════════════
            "voice": {
                "name": "en-US-AndrewMultilingualNeural",  # Azure Neural Voice
                "type": "azure-standard"                    # Voice type
            }
            
            # ❌ NO instructions - Azure Agent already has them!
            # ❌ NO model - configured in Azure Portal
            # ❌ NO temperature - configured in Azure Portal
            # ❌ NO max_tokens - configured in Azure Portal
        }
    }
    
    # Send configuration to Azure as JSON
    await azure_ws.send(json.dumps(config_message))
    print("✅ Session configuration sent to Azure")
    print("🎙️ Ready to send/receive audio!")
```

### **4.3: Configuration Settings Explained**

| Setting | Value | Purpose |
|---------|-------|---------|
| **modalities** | `["text", "audio"]` | Enable both text and voice communication |
| **turn_detection.type** | `"azure_semantic_vad"` | Detect when user stops speaking |
| **input_audio_transcription.model** | `"azure-speech"` | Speech-to-Text service |
| **input_audio_transcription.language** | `"en-US"` | Transcription language |
| **input_audio_noise_reduction.type** | `"azure_deep_noise_suppression"` | Remove background noise |
| **input_audio_echo_cancellation.type** | `"server_echo_cancellation"` | Prevent audio feedback |
| **avatar.character** | `"jeff"` | Visual avatar name |
| **avatar.style** | `"business"` | Avatar appearance |
| **voice.name** | `"en-US-AndrewMultilingualNeural"` | AI response voice |
| **voice.type** | `"azure-standard"` | Voice quality tier |

---

## Connection Flow Diagram

### **Complete Flow from Start to Finish:**

```
┌──────────────────────────────────────────────────────────────────┐
│                    STEP 1: Create Agent in Portal                │
│                                                                   │
│  https://ai.azure.com → Agents → + New Agent                     │
│                                                                   │
│  ✅ Set Instructions: "You are a professional banker..."         │
│  ✅ Choose Model: gpt-4o                                          │
│  ✅ Set Temperature: 0.7                                          │
│  ✅ Copy Agent ID: asst_abc123...                                │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    STEP 2: Configure .env File                    │
│                                                                   │
│  USE_AZURE_AI_AGENTS=true                                         │
│  AGENT_ID=asst_abc123...                                          │
│  AZURE_AI_PROJECT_NAME=your-project                               │
│  AZURE_AI_RESOURCE_NAME=your-resource                             │
│  AZURE_OPENAI_API_KEY=your-key                                    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                  STEP 3: Connect to Azure WebSocket              │
│                                                                   │
│  url = "wss://{resource}.services.ai.azure.com/voice-live/       │
│         realtime?api-version=2025-10-01                           │
│         &agent-id={agent_id}&project-id={project}"                │
│                                                                   │
│  azure_ws = await websockets.connect(                             │
│      url,                                                         │
│      additional_headers={"api-key": api_key}                      │
│  )                                                                │
│                                                                   │
│  ✅ WebSocket connection established!                            │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│               STEP 4: Send Session Configuration                  │
│                                                                   │
│  config = {                                                       │
│      "type": "session.update",                                    │
│      "session": {                                                 │
│          "modalities": ["text", "audio"],                         │
│          "turn_detection": {"type": "azure_semantic_vad"},        │
│          "input_audio_transcription": {                           │
│              "model": "azure-speech",                             │
│              "language": "en-US"                                  │
│          },                                                       │
│          "input_audio_noise_reduction": {...},                    │
│          "input_audio_echo_cancellation": {...},                  │
│          "avatar": {"character": "jeff", "style": "business"},    │
│          "voice": {                                               │
│              "name": "en-US-AndrewMultilingualNeural",            │
│              "type": "azure-standard"                             │
│          }                                                        │
│          // ❌ NO instructions, model, temperature               │
│          // → Already in Azure Agent!                            │
│      }                                                            │
│  }                                                                │
│                                                                   │
│  await azure_ws.send(json.dumps(config))                          │
│                                                                   │
│  ✅ Azure is configured and ready!                               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                   STEP 5: Send/Receive Audio                      │
│                                                                   │
│  # Send user's audio to Azure                                    │
│  await azure_ws.send(json.dumps({                                 │
│      "type": "input_audio_buffer.append",                         │
│      "audio": "base64_audio_data..."                              │
│  }))                                                              │
│                                                                   │
│  # Receive AI's audio response                                   │
│  async for message in azure_ws:                                  │
│      msg = json.loads(message)                                    │
│      if msg["type"] == "response.audio.delta":                    │
│          audio_data = msg["delta"]  # Base64 audio               │
│          # Play to user's speakers                               │
│                                                                   │
│  🎙️ Voice conversation is now active!                           │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Start Checklist

### **Azure Portal Setup:**
- [ ] Create Azure OpenAI resource
- [ ] Deploy gpt-4o model in Azure OpenAI
- [ ] Create Azure AI Foundry Hub
- [ ] Create Azure AI Foundry Project
- [ ] Create Azure AI Agent with:
  - [ ] Instructions (system prompt)
  - [ ] Model selection (gpt-4o)
  - [ ] Temperature (0.7)
- [ ] Copy Agent ID (starts with `asst_`)

### **Backend Configuration:**
- [ ] Create `.env` file
- [ ] Set `USE_AZURE_AI_AGENTS=true`
- [ ] Set `AGENT_ID=asst_your_id`
- [ ] Set `AZURE_AI_PROJECT_NAME`
- [ ] Set `AZURE_AI_RESOURCE_NAME`
- [ ] Set `AZURE_OPENAI_API_KEY`

### **Code Implementation:**
- [ ] Install `websockets` library (`pip install websockets`)
- [ ] Build WebSocket URL with agent-id and project-id
- [ ] Connect to Azure (`websockets.connect()`)
- [ ] Send session configuration (audio/voice settings only)
- [ ] Start sending/receiving audio messages

---

## Common Questions

### **Q: What if I want to update the AI instructions?**
A: Go to Azure AI Foundry Portal → Your Agent → Edit Instructions → Save. 
Changes take effect immediately - no code deployment needed! ✅

### **Q: Do I need to send instructions in the session.update message?**
A: No! The agent already has instructions from the Azure Portal. 
Only send audio/voice configuration.

### **Q: Can I use multiple agents?**
A: Yes! Create multiple agents in the Portal, each with different instructions. 
Use different agent IDs to switch between them.

### **Q: What's the difference between `.services.ai.azure.com` and `.cognitiveservices.azure.com`?**
A: 
- `.services.ai.azure.com` = Azure AI Foundry (use with agents)
- `.cognitiveservices.azure.com` = Traditional Azure OpenAI (direct model access)

For Azure AI Agents, always use `.services.ai.azure.com`!

### **Q: Why does my connection fail?**
Common issues:
- ❌ Wrong API key → Check Azure Portal → Keys and Endpoint
- ❌ Wrong agent ID → Check it starts with `asst_`
- ❌ Wrong project name → Check Azure AI Foundry → Project Settings
- ❌ Wrong domain → Use `.services.ai.azure.com` not `.cognitiveservices.azure.com`

---

## Complete Working Example

```python
import asyncio
import websockets
import json

# Configuration
AZURE_AI_RESOURCE_NAME = "your-resource-name"
AZURE_OPENAI_API_KEY = "your-api-key"
AGENT_ID = "asst_wgsM81Hm1FuLOJemAeEfrYQr"
AZURE_AI_PROJECT_NAME = "your-project-name"


async def main():
    """Complete example: Connect and configure Azure Voice API"""
    
    # STEP 1: Build WebSocket URL
    url = (
        f"wss://{AZURE_AI_RESOURCE_NAME}.services.ai.azure.com/"
        f"voice-live/realtime"
        f"?api-version=2025-10-01"
        f"&agent-id={AGENT_ID}"
        f"&project-id={AZURE_AI_PROJECT_NAME}"
    )
    
    # STEP 2: Connect to Azure
    print("🔗 Connecting to Azure Voice API...")
    azure_ws = await websockets.connect(
        url,
        additional_headers={"api-key": AZURE_OPENAI_API_KEY}
    )
    print("✅ Connected!")
    
    # STEP 3: Send session configuration
    config = {
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "turn_detection": {"type": "azure_semantic_vad"},
            "input_audio_transcription": {
                "model": "azure-speech",
                "language": "en-US"
            },
            "input_audio_noise_reduction": {
                "type": "azure_deep_noise_suppression"
            },
            "input_audio_echo_cancellation": {
                "type": "server_echo_cancellation"
            },
            "avatar": {
                "character": "jeff",
                "style": "business"
            },
            "voice": {
                "name": "en-US-AndrewMultilingualNeural",
                "type": "azure-standard"
            }
        }
    }
    
    await azure_ws.send(json.dumps(config))
    print("✅ Configuration sent!")
    print("🎙️ Ready for audio communication!")
    
    # STEP 4: Now you can send/receive audio
    # Your audio streaming logic goes here...
    
    # Keep connection open
    await asyncio.sleep(60)
    await azure_ws.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Summary

**The 4-Step Process:**

1. ✅ **Create Agent in Azure Portal** - Set instructions, model, temperature
2. ✅ **Configure .env** - Add agent ID and Azure credentials
3. ✅ **Connect to Azure** - WebSocket with agent-id parameter
4. ✅ **Send Configuration** - Audio/voice settings only (no instructions!)

**Key Advantages:**
- 🎯 Instructions managed in Azure Portal (no code deployment to update)
- 🎯 Centralized configuration
- 🎯 Easy for non-developers to update AI behavior
- 🎯 Perfect for production environments

---

**🎉 You're ready to build Azure AI Voice applications!**

For detailed WebSocket proxy implementation, frontend audio processing, and complete application code, see **TEACHING-GUIDE.md**.

