# 🎓 Step-by-Step Guide: Building an Azure AI Voice Agent Solution

## 📚 Table of Contents
1. [Prerequisites & Setup](#prerequisites--setup)
2. [Project Structure Overview](#project-structure-overview)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Testing Your Application](#testing-your-application)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites & Setup

### What You'll Need:
- **Python 3.8+** installed
- **Azure Account** with:
  - Azure AI Foundry Hub & Project
  - Azure OpenAI Service (GPT-4o deployment)
  - Azure Speech Services
- **Basic Python knowledge** (functions, classes, async/await)
- **Text editor** (VS Code recommended)

### Initial Setup Commands:
```bash
# Create project folder
mkdir voice-agent-backend
cd voice-agent-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Create folder structure
mkdir -p backend/src/services
mkdir -p data/scenarios
mkdir static
```

---

## Project Structure Overview

```
voice-agent-backend/
├── backend/
│   ├── requirements.txt          # 📦 Python dependencies
│   ├── src/
│   │   ├── config.py            # ⚙️ Configuration management
│   │   ├── app.py               # 🚀 Main Flask application
│   │   └── services/
│   │       ├── managers.py      # 🎭 Agent & scenario management
│   │       └── websocket_handler.py  # 🔌 WebSocket proxy
├── data/
│   └── scenarios/               # 📝 Scenario YAML files
├── static/                      # 🌐 Frontend files (optional)
└── .env                         # 🔐 Environment variables
```

---

## Backend Implementation

### **STEP 1: Install Dependencies** (5 minutes)

Create `backend/requirements.txt`:

```txt
# Azure SDK for AI Projects
azure-ai-projects>=1.0.0

# Azure Authentication
azure-identity>=1.15.0

# Azure Speech Services (for pronunciation assessment)
azure-cognitiveservices-speech==1.45.0

# OpenAI Client (works with Azure OpenAI)
openai==1.102.0

# Web Framework
flask==3.1.2
flask-sock==0.7.0

# WebSocket client for Azure connection
websockets==15.0.1

# Utilities
python-dotenv==1.1.1
pyyaml==6.0.2
```

**Install:**
```bash
pip install -r backend/requirements.txt
```

**🎯 Key Dependencies:**
- `flask` - Web server for API endpoints
- `flask-sock` - WebSocket support in Flask
- `websockets` - Async WebSocket client for Azure
- `azure-ai-projects` - Azure AI Foundry SDK
- `openai` - OpenAI/Azure OpenAI client

---

### **STEP 2: Configuration Management** (10 minutes)

**File:** `backend/src/config.py`

**Purpose:** Centralize all environment variables and settings in one place.

**Key Concepts:**
- Load environment variables from `.env` file
- Provide default values
- Type conversion (string to bool, int)

**Complete Code:**

```python
import os
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
# This reads your .env file and makes variables available via os.getenv()
load_dotenv()

# Default values as constants
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"
DEFAULT_REGION = "swedencentral"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_API_VERSION = "2024-12-01-preview"
DEFAULT_SPEECH_LANGUAGE = "ar-SA,en-US"
DEFAULT_INPUT_TRANSCRIPTION_MODEL = "azure-speech"
DEFAULT_INPUT_NOISE_REDUCTION_TYPE = "azure_deep_noise_suppression"
DEFAULT_VOICE_NAME = "en-US-AndrewMultilingualNeural"
DEFAULT_VOICE_TYPE = "azure-standard"
DEFAULT_AVATAR_CHARACTER = "jeff"
DEFAULT_AVATAR_STYLE = "business"

class Config:
    """
    Application configuration from environment variables.
    
    This class centralizes all configuration so you don't need to call
    os.getenv() everywhere in your code. Instead, you use config["key"].
    """
    
    def __init__(self):
        """Initialize and load all configuration on startup."""
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load all configuration values from environment variables.
        
        Pattern: os.getenv("ENV_VAR_NAME", "default_value")
        - First parameter: Name of environment variable (from .env file)
        - Second parameter: Default value if not set
        
        Returns:
            Dictionary with all configuration keys and values
        """
        return {
            # ═══════════════════════════════════════════════════════════
            # Azure AI Foundry Settings
            # ═══════════════════════════════════════════════════════════
            
            # Your Azure AI resource name (e.g., "my-ai-resource")
            # This becomes part of the Azure endpoint URL
            # Example: my-ai-resource.services.ai.azure.com
            "azure_ai_resource_name": os.getenv("AZURE_AI_RESOURCE_NAME", ""),
            
            # Your AI Foundry project name (e.g., "my-project")
            # Used when connecting to Azure AI Foundry agents
            "azure_ai_project_name": os.getenv("AZURE_AI_PROJECT_NAME", ""),
            
            # Boolean: Use Azure AI Foundry agents (true) or direct OpenAI models (false)
            # "false" string converted to False boolean
            # "true" string converted to True boolean
            "use_azure_ai_agents": os.getenv("USE_AZURE_AI_AGENTS", "false").lower() == "true",
            
            # Pre-configured Azure AI agent ID (e.g., "asst_abc123...")
            # Only needed if use_azure_ai_agents is true
            "agent_id": os.getenv("AGENT_ID", ""),
            
            # ═══════════════════════════════════════════════════════════
            # Azure OpenAI Settings
            # ═══════════════════════════════════════════════════════════
            
            # Full Azure OpenAI endpoint URL
            # Example: "https://my-resource.openai.azure.com/"
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            
            # API key for Azure OpenAI authentication
            # CRITICAL: Never commit this to git! Keep in .env file only
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
            
            # GPT model deployment name in Azure (e.g., "gpt-4o", "gpt-4", "gpt-35-turbo")
            # Must match your deployment name in Azure Portal
            "model_deployment_name": os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o"),
            
            # ═══════════════════════════════════════════════════════════
            # Server Settings
            # ═══════════════════════════════════════════════════════════
            
            # Port number for Flask server (default: 8000)
            # Convert string to integer since os.getenv() returns strings
            "port": int(os.getenv("PORT", "8000")),
            
            # Host to bind server to
            # "0.0.0.0" = accessible from any network interface (needed for Docker/Azure)
            # "127.0.0.1" = only accessible from localhost
            "host": os.getenv("HOST", "0.0.0.0"),
            
            # ═══════════════════════════════════════════════════════════
            # Voice & Avatar Settings
            # ═══════════════════════════════════════════════════════════
            
            # Azure Neural Voice name for text-to-speech
            # This is the voice the AI agent will use when speaking
            # Example: "en-US-AndrewMultilingualNeural" (male voice)
            # See Azure Speech Studio for all available voices
            "azure_voice_name": os.getenv("AZURE_VOICE_NAME", "en-US-AndrewMultilingualNeural"),
            
            # Avatar character appearance
            # Options: "lisa", "jeff", etc. (see Azure documentation)
            "azure_avatar_character": os.getenv("AZURE_AVATAR_CHARACTER", "jeff"),
            
            # Avatar style/clothing
            # Options: "casual", "business", etc.
            "azure_avatar_style": os.getenv("AZURE_AVATAR_STYLE", "business"),
        }
    
    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value by key using dictionary syntax.
        
        Usage: config["azure_openai_api_key"]
        This is called when you use config[key]
        """
        return self._config.get(key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration with optional default fallback.
        
        Usage: config.get("some_key", "default_value")
        Returns default if key doesn't exist
        """
        return self._config.get(key, default)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL CONFIG INSTANCE
# ═══════════════════════════════════════════════════════════════════
# Create ONE instance that will be imported everywhere
# This means config is loaded once at startup and shared across all files
config = Config()

# Now in other files, you can do:
# from src.config import config
# api_key = config["azure_openai_api_key"]
```

**🎓 Teaching Points:**
1. **Environment Variables:** Never hardcode credentials!
2. **Default Values:** Make development easier with sensible defaults
3. **Type Conversion:** Environment variables are strings, convert them
4. **Singleton Pattern:** One global `config` object used everywhere
5. **Dictionary Access:** `config["key"]` is cleaner than `os.getenv()` everywhere

**How config[] Works:**
```python
# When you write this in any file:
from src.config import config
api_key = config["azure_openai_api_key"]

# It's equivalent to:
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")

# But config[] is better because:
# ✅ Centralized in one place
# ✅ Type conversion done once (string → int, bool)
# ✅ Easy to add validation or logging
# ✅ Can be mocked for testing
```

**Create `.env` file in project root:**
```env
# ═══════════════════════════════════════════════════════════
# REQUIRED: Core Azure Settings (Get from Azure Portal)
# ═══════════════════════════════════════════════════════════
AZURE_AI_RESOURCE_NAME=your-resource-name
AZURE_OPENAI_API_KEY=your-api-key-here

# ═══════════════════════════════════════════════════════════
# Model Configuration
# ═══════════════════════════════════════════════════════════
MODEL_DEPLOYMENT_NAME=gpt-4o

# ═══════════════════════════════════════════════════════════
# Choose Mode: Azure AI Agents (true) or Direct Model (false)
# ═══════════════════════════════════════════════════════════
USE_AZURE_AI_AGENTS=false

# If USE_AZURE_AI_AGENTS=true, also set:
# AGENT_ID=asst_your-agent-id-here
# AZURE_AI_PROJECT_NAME=your-project-name
```

---

### **STEP 3: Agent Configuration - Two Approaches** (20 minutes)

**File:** `backend/src/services/managers.py`

**Purpose:** Configure AI agents - either using Azure AI Foundry agents OR local configuration with YAML files.

---

## 🔀 **Two Approaches Explained**

Your application supports **TWO different ways** to configure the AI agent:

### **Approach A: Azure AI Foundry Agents** (Recommended for Production)
- Agent is **pre-created** in Azure AI Foundry Portal
- Instructions, model, and settings are **configured in Azure**
- Backend just uses the `AGENT_ID` to connect
- ✅ Easier to update (no code deployment needed)
- ✅ Better for production (centralized management)

### **Approach B: Local YAML Configuration** (Good for Development)
- Agent configuration is stored in **YAML files** locally
- Backend **sends instructions** to Azure Voice Live API at runtime
- ⚠️ Instructions are in code (requires redeployment to update)
- ✅ Good for testing different configurations quickly

---

## 📋 **Configuration Setting**

In your `.env` file:

```bash
# Set to 'true' for Approach A (Azure AI Foundry)
# Set to 'false' for Approach B (Local YAML)
USE_AZURE_AI_AGENTS=false  # ← Controls which approach is used
```

---

## **Approach A: Using Azure AI Foundry Agents**

### **Setup in Azure Portal:**

1. Go to Azure AI Foundry Portal
2. Create an Agent with:
   - Name: "NBK Banking Assistant"
   - Model: gpt-4o
   - Instructions: Your system prompt
   - Temperature: 0.7
3. Copy the Agent ID (looks like: `asst_abc123...`)

### **Configuration in `.env`:**

```bash
USE_AZURE_AI_AGENTS=true
AGENT_ID=asst_your_agent_id_from_azure
AZURE_AI_PROJECT_NAME=your-project-name
AZURE_AI_RESOURCE_NAME=your-resource-name
```

### **Code Implementation:**

```python
from azure.identity import DefaultAzureCredential
from src.config import config

class AgentManager:
    """Manages AI agents."""
    
    def __init__(self):
        """Initialize agent manager."""
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.use_azure_ai_agents = config["use_azure_ai_agents"]
        
        if self.use_azure_ai_agents:
            logger.info("Using Azure AI Foundry agents")
        else:
            logger.info("Using local YAML configuration")
    
    def create_agent(self, scenario_id: str, scenario_data: Dict[str, Any]) -> str:
        """
        Create agent configuration.
        
        For Azure AI agents: Uses pre-configured agent from Azure
        For Local agents: Builds config from YAML file
        """
        if self.use_azure_ai_agents:
            # APPROACH A: Use existing Azure AI agent
            return self._create_azure_agent(scenario_id, scenario_data)
        else:
            # APPROACH B: Use local YAML configuration
            return self._create_local_agent(scenario_id, scenario_data)
    
    def _create_azure_agent(self, scenario_id: str, scenario_data: Dict[str, Any]) -> str:
        """
        Use existing Azure AI Foundry agent.
        
        The agent is already configured in Azure Portal with:
        - Instructions (system prompt)
        - Model (gpt-4o)
        - Temperature, max_tokens, etc.
        
        We just need the AGENT_ID to connect to it.
        """
        # Get the pre-configured agent ID from .env
        agent_id = config.get("agent_id", "")
        
        if not agent_id:
            raise ValueError(
                "AGENT_ID not configured. "
                "Please create an agent in Azure AI Foundry and set AGENT_ID in .env"
            )
        
        logger.info(f"Using Azure AI agent: {agent_id} for scenario: {scenario_id}")
        
        # Store minimal config (agent is managed in Azure)
        self.agents[agent_id] = {
            "scenario_id": scenario_id,
            "is_azure_agent": True,  # ← Key flag!
            "azure_agent_id": agent_id,
            # Instructions, model, temp are in Azure - NOT sent from backend
        }
        
        return agent_id
```

**🎯 Key Points for Approach A:**
- ✅ YAML `name` and `description` used for UI display only
- ❌ YAML `messages[0].content` (instructions) NOT used - Azure has them
- ❌ YAML `model` NOT used - configured in Azure
- ❌ YAML `temperature` NOT used - configured in Azure
- ✅ Agent ID from `.env` is used to connect

---

## **Approach B: Using Local YAML Configuration**

### **Configuration in `.env`:**

```bash
USE_AZURE_AI_AGENTS=false  # ← Use local configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
MODEL_DEPLOYMENT_NAME=gpt-4o
```

### **Create YAML File:** `data/scenarios/nbk-banking-role-play.prompt.yml`

```yaml
name: "NBK Banking Customer Service"
description: "Professional banking customer service for National Bank of Kuwait"

messages:
  - role: system
    content: |
      You are a professional customer service representative for NBK.
      
      Your role:
      - Assist customers with banking inquiries
      - Provide accurate information about NBK services
      - Communicate clearly in Arabic and English
      - Keep responses brief (2-3 sentences max)
      - Never ask for sensitive credentials
      
      Remember: Professional, helpful, and trustworthy!

model: gpt-4o
modelParameters:
  temperature: 0.7
  max_tokens: 2000
```

### **Code Implementation:**

```python
def _create_local_agent(self, scenario_id: str, scenario_data: Dict[str, Any]) -> str:
    """
    Create local agent from YAML configuration.
    
    All settings from YAML will be sent to Azure Voice Live API
    when the WebSocket session starts.
    """
    # Generate unique ID for this agent instance
    agent_id = f"local-agent-{uuid.uuid4().hex[:8]}"
    
    # Extract configuration from YAML
    scenario_instructions = scenario_data.get("messages", [{}])[0].get("content", "")
    model_name = scenario_data.get("model", config["model_deployment_name"])
    temperature = scenario_data.get("modelParameters", {}).get("temperature", 0.7)
    max_tokens = scenario_data.get("modelParameters", {}).get("max_tokens", 2000)
    
    # Store complete configuration (will be sent to Azure)
    self.agents[agent_id] = {
        "scenario_id": scenario_id,
        "is_azure_agent": False,  # ← Key flag!
        "instructions": scenario_instructions,  # ← Sent to Azure
        "model": model_name,                     # ← Sent to Azure
        "temperature": temperature,              # ← Sent to Azure
        "max_tokens": max_tokens,                # ← Sent to Azure
    }
    
    logger.info(f"Created local agent: {agent_id} for scenario: {scenario_id}")
    return agent_id
```

**🎯 Key Points for Approach B:**
- ✅ YAML `name` and `description` used for UI display
- ✅ YAML `messages[0].content` (instructions) SENT to Azure
- ✅ YAML `model` SENT to Azure
- ✅ YAML `temperature` and `max_tokens` SENT to Azure
- ✅ Configuration sent in `session.update` message via WebSocket

---

## **How the Backend Sends Local Config to Azure**

When using **Approach B**, the WebSocket handler sends configuration to Azure Voice Live API.

### **Complete Configuration Message Example:**

Here's what gets sent to Azure with **actual values** (not variable names):

```json
{
  "type": "session.update",
  "session": {
    "modalities": ["text", "audio"],
    
    "turn_detection": {
      "type": "azure_semantic_vad"
    },
    
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
    },
    
    "instructions": "You are a professional customer service representative for National Bank of Kuwait (NBK).\n\nYour role:\n- Assist customers with banking inquiries\n- Provide accurate information about NBK services\n- Communicate clearly in Arabic and English\n- Keep responses brief (2-3 sentences max)\n- Never ask for sensitive credentials\n\nRemember: Professional, helpful, and trustworthy!",
    
    "model": "gpt-4o",
    
    "temperature": 0.7,
    
    "max_response_output_tokens": 2000
  }
}
```

### **Breaking Down the Configuration:**

#### **🎙️ Audio & Voice Settings** (Always Sent - Both Approaches)

| Setting | Value | Purpose |
|---------|-------|---------|
| **modalities** | `["text", "audio"]` | Enable both text and voice communication |
| **turn_detection.type** | `"azure_semantic_vad"` | Detect when user stops speaking (Voice Activity Detection) |
| **input_audio_transcription.model** | `"azure-speech"` | Speech-to-Text model for converting voice to text |
| **input_audio_transcription.language** | `"en-US"` | Transcribe audio in US English |
| **input_audio_noise_reduction.type** | `"azure_deep_noise_suppression"` | Remove background noise from user's microphone |
| **input_audio_echo_cancellation.type** | `"server_echo_cancellation"` | Prevent echo/feedback in audio |
| **avatar.character** | `"jeff"` | Visual avatar character name |
| **avatar.style** | `"business"` | Avatar appearance style |
| **voice.name** | `"en-US-AndrewMultilingualNeural"` | Azure Neural Voice for AI responses |
| **voice.type** | `"azure-standard"` | Voice type (standard Azure neural TTS) |

#### **🤖 AI Agent Settings** (Only for Approach B - Local Config)

| Setting | Value | Purpose |
|---------|-------|---------|
| **instructions** | `"You are a professional customer service representative..."` | System prompt defining AI's personality and behavior |
| **model** | `"gpt-4o"` | GPT model deployment name from Azure OpenAI |
| **temperature** | `0.7` | Creativity level (0.0 = deterministic, 1.0 = creative) |
| **max_response_output_tokens** | `2000` | Maximum length of AI responses |

---

### **Code Implementation:**

```python
# In websocket_handler.py
async def _send_initial_config(
    self,
    azure_ws: websockets.asyncio.client.ClientConnection,
    agent_config: Optional[Dict[str, Any]],
) -> None:
    """Send session configuration to Azure Voice Live API."""
    
    # Step 1: Build base configuration (audio/voice settings)
    config_message = self._build_session_config()
    # Returns the audio/voice settings shown above
    
    # Step 2: Add AI agent settings ONLY for local configuration
    if agent_config and not agent_config.get("is_azure_agent"):
        # Add these 4 fields for local agents:
        config_message["session"]["instructions"] = agent_config["instructions"]
        config_message["session"]["model"] = agent_config["model"]
        config_message["session"]["temperature"] = agent_config["temperature"]
        config_message["session"]["max_response_output_tokens"] = agent_config["max_tokens"]
    
    # Step 3: Send complete configuration to Azure as JSON
    await azure_ws.send(json.dumps(config_message))
```

---

### **What Gets Sent in Each Approach:**

#### **Approach A: Azure AI Foundry Agent** (`is_azure_agent=True`)
```json
{
  "type": "session.update",
  "session": {
    "modalities": ["text", "audio"],
    "turn_detection": {"type": "azure_semantic_vad"},
    "input_audio_transcription": {"model": "azure-speech", "language": "en-US"},
    "input_audio_noise_reduction": {"type": "azure_deep_noise_suppression"},
    "input_audio_echo_cancellation": {"type": "server_echo_cancellation"},
    "avatar": {"character": "jeff", "style": "business"},
    "voice": {"name": "en-US-AndrewMultilingualNeural", "type": "azure-standard"}
    
    // ❌ NO instructions - Azure has them from Portal
    // ❌ NO model - configured in Azure
    // ❌ NO temperature - configured in Azure
    // ❌ NO max_tokens - configured in Azure
  }
}
```

#### **Approach B: Local YAML Configuration** (`is_azure_agent=False`)
```json
{
  "type": "session.update",
  "session": {
    "modalities": ["text", "audio"],
    "turn_detection": {"type": "azure_semantic_vad"},
    "input_audio_transcription": {"model": "azure-speech", "language": "en-US"},
    "input_audio_noise_reduction": {"type": "azure_deep_noise_suppression"},
    "input_audio_echo_cancellation": {"type": "server_echo_cancellation"},
    "avatar": {"character": "jeff", "style": "business"},
    "voice": {"name": "en-US-AndrewMultilingualNeural", "type": "azure-standard"},
    
    // ✅ ADDED: AI behavior from YAML file
    "instructions": "You are a professional customer service representative...",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_response_output_tokens": 2000
  }
}
```

---

### **🎯 Key Takeaway:**

**Approach A** = "Hey Azure, use agent ID `asst_abc123` with settings you already have"
**Approach B** = "Hey Azure, here's the complete AI configuration to use for this session"

---

## **Comparison Table**

| Feature | Approach A: Azure AI Foundry | Approach B: Local YAML |
|---------|------------------------------|------------------------|
| **Configuration Location** | Azure Portal | YAML files in code |
| **Instructions Source** | Azure | YAML `messages[0].content` |
| **Model Selection** | Azure | YAML `model` |
| **Temperature** | Azure | YAML `modelParameters.temperature` |
| **Update Process** | Change in Portal (instant) | Change YAML + redeploy |
| **Best For** | Production | Development/Testing |
| **Backend Complexity** | Simple (just connects) | Sends full config |

---

## **Recommendation for NBK Banking:**

**Use Approach A (Azure AI Foundry)** because:
1. ✅ Instructions can be updated without code deployment
2. ✅ Better security (credentials not in YAML)
3. ✅ Centralized management in Azure Portal
4. ✅ Easier for non-developers to update prompts

**Use Approach B (Local YAML)** when:
- 🔧 Rapidly testing different prompts during development
- 🔧 Want version control for instructions (Git)
- 🔧 Need multiple scenario variations

---

### **STEP 4: WebSocket Proxy Handler** (25 minutes) ⭐ **MOST IMPORTANT**

**File:** `backend/src/services/websocket_handler.py`

**Purpose:** Proxy WebSocket connections between client and Azure Voice API.

**This is the CORE of your voice agent!**

**Simplified Version for Beginners:**

```python
import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional
import websockets
import simple_websocket.ws
from src.config import config

logger = logging.getLogger(__name__)

class VoiceProxyHandler:
    """Handles WebSocket proxy between client and Azure Voice API."""
    
    def __init__(self, agent_manager):
        """Initialize with agent manager."""
        self.agent_manager = agent_manager
    
    async def handle_connection(self, client_ws: simple_websocket.ws.Server) -> None:
        """
        Main handler for client connections.
        
        Flow:
        1. Get agent ID from client
        2. Connect to Azure
        3. Forward messages bidirectionally
        4. Cleanup on disconnect
        """
        azure_ws = None
        
        try:
            # Step 1: Get agent ID from first client message
            agent_id = await self._get_agent_id_from_client(client_ws)
            
            # Step 2: Connect to Azure Voice API
            azure_ws = await self._connect_to_azure(agent_id)
            if not azure_ws:
                await self._send_error(client_ws, "Failed to connect to Azure")
                return
            
            # Step 3: Notify client we're connected
            await self._send_message(client_ws, {
                "type": "proxy.connected",
                "message": "Connected to Azure Voice API"
            })
            
            # Step 4: Start forwarding messages
            await self._forward_messages(client_ws, azure_ws)
        
        except Exception as e:
            logger.error(f"Connection error: {e}")
            await self._send_error(client_ws, str(e))
        
        finally:
            # Always cleanup
            if azure_ws:
                await azure_ws.close()
    
    async def _get_agent_id_from_client(self, client_ws) -> Optional[str]:
        """Extract agent ID from first client message."""
        try:
            # Wait for first message from client
            first_message = await asyncio.get_event_loop().run_in_executor(
                None, client_ws.receive
            )
            
            if first_message:
                msg = json.loads(first_message)
                # Expect: {"type": "session.update", "session": {"agent_id": "..."}}
                return msg.get("session", {}).get("agent_id")
        
        except Exception as e:
            logger.error(f"Error getting agent ID: {e}")
        
        return None
    
    async def _connect_to_azure(self, agent_id: Optional[str]):
        """
        Connect to Azure Voice API via WebSocket.
        
        This establishes a WebSocket connection to Azure's voice API,
        which enables real-time voice conversations with AI.
        
        Args:
            agent_id: Optional agent identifier for configuration
        
        Returns:
            WebSocket connection to Azure, or None if failed
        """
        try:
            # ═══════════════════════════════════════════════════════════
            # Step 1: Build Azure WebSocket URL
            # ═══════════════════════════════════════════════════════════
            
            # Get resource name from config (from .env file)
            # Example: "my-ai-resource"
            # config["azure_ai_resource_name"] = os.getenv("AZURE_AI_RESOURCE_NAME")
            resource_name = config["azure_ai_resource_name"]
            
            # Get API key from config (from .env file)
            # config["azure_openai_api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
            api_key = config["azure_openai_api_key"]
            
            if not api_key:
                logger.error("No API key configured")
                return None
            
            # ═══════════════════════════════════════════════════════════
            # Step 2: Choose URL based on agent type
            # ═══════════════════════════════════════════════════════════
            
            # Check mode from config (from .env: USE_AZURE_AI_AGENTS=true/false)
            # config.get("use_azure_ai_agents") returns True or False
            if config.get("use_azure_ai_agents"):
                # ───────────────────────────────────────────────────────
                # Option 1: Azure AI Foundry (newer platform)
                # ───────────────────────────────────────────────────────
                # URL pattern: wss://{resource}.services.ai.azure.com/voice-live/realtime
                
                # config["agent_id"] = os.getenv("AGENT_ID")
                # Example: "asst_abc123def456"
                agent_id_param = config["agent_id"]
                
                # config["azure_ai_project_name"] = os.getenv("AZURE_AI_PROJECT_NAME")
                # Example: "my-voice-project"
                project_name = config["azure_ai_project_name"]
                
                # Build complete URL with query parameters
                url = (
                    f"wss://{resource_name}.services.ai.azure.com/"
                    f"voice-live/realtime"
                    f"?api-version=2025-10-01"  # API version (hardcoded, Azure requirement)
                    f"&agent-id={agent_id_param}"  # Your pre-configured agent
                    f"&project-id={project_name}"  # Your AI Foundry project
                )
                # Example result:
                # wss://my-ai-resource.services.ai.azure.com/voice-live/realtime?api-version=2025-10-01&agent-id=asst_abc123&project-id=my-project
                
            else:
                # ───────────────────────────────────────────────────────
                # Option 2: Azure Cognitive Services (traditional OpenAI)
                # ───────────────────────────────────────────────────────
                # URL pattern: wss://{resource}.cognitiveservices.azure.com/voice-agent/realtime
                
                # config["model_deployment_name"] = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
                # Example: "gpt-4o" or "gpt-35-turbo"
                model_name = config["model_deployment_name"]
                
                # Build complete URL with query parameters
                url = (
                    f"wss://{resource_name}.cognitiveservices.azure.com/"
                    f"voice-agent/realtime"
                    f"?api-version=2025-10-01"  # API version (hardcoded, Azure requirement)
                    f"&model={model_name}"  # Which GPT model to use
                )
                # Example result:
                # wss://my-ai-resource.cognitiveservices.azure.com/voice-agent/realtime?api-version=2025-10-01&model=gpt-4o
            
            # ═══════════════════════════════════════════════════════════
            # Step 3: Connect with authentication
            # ═══════════════════════════════════════════════════════════
            
            # Azure requires API key in HTTP headers for authentication
            headers = {"api-key": api_key}
            
            # Establish WebSocket connection
            # This is async, so we use 'await'
            azure_ws = await websockets.connect(url, additional_headers=headers)
            
            logger.info(f"Connected to Azure with agent: {agent_id or 'default'}")
            
            # ═══════════════════════════════════════════════════════════
            # Step 4: Send initial configuration to Azure
            # ═══════════════════════════════════════════════════════════
            await self._send_session_config(azure_ws, agent_id)
            
            return azure_ws
        
        except Exception as e:
            logger.error(f"Azure connection failed: {e}")
            return None
    
    async def _send_session_config(self, azure_ws, agent_id: Optional[str]):
        """
        Send initial configuration to Azure.
        
        This tells Azure how to configure the voice session:
        - Which voice to use
        - What avatar to show
        - Audio processing settings
        - Agent instructions (for local agents only)
        
        Args:
            azure_ws: Connected Azure WebSocket
            agent_id: Optional agent ID to get configuration
        """
        
        # ═══════════════════════════════════════════════════════════
        # Step 1: Get agent configuration if available
        # ═══════════════════════════════════════════════════════════
        
        # If agent_id provided, get its configuration from AgentManager
        # Otherwise, agent_config = None (will use Azure AI agent config)
        agent_config = self.agent_manager.get_agent(agent_id) if agent_id else None
        
        # ═══════════════════════════════════════════════════════════
        # Step 2: Build session configuration message
        # ═══════════════════════════════════════════════════════════
        
        config_message = {
            # Message type: tells Azure this is a configuration update
            "type": "session.update",
            
            # Session configuration object
            "session": {
                # ───────────────────────────────────────────────────
                # Communication modes enabled
                # ───────────────────────────────────────────────────
                # ["text", "audio"] = enable both text and voice input/output
                # Hardcoded list - Azure requirement
                "modalities": ["text", "audio"],
                
                # ───────────────────────────────────────────────────
                # Turn detection (when AI should start/stop talking)
                # ───────────────────────────────────────────────────
                "turn_detection": {
                    # "azure_semantic_vad" = Voice Activity Detection
                    # Azure AI understands natural pauses in speech
                    # Hardcoded - this is the best option available
                    "type": "azure_semantic_vad"
                },
                
                # ───────────────────────────────────────────────────
                # Audio preprocessing settings
                # ───────────────────────────────────────────────────
                "input_audio_noise_reduction": {
                    # Remove background noise using Azure AI
                    # "azure_deep_noise_suppression" = use Azure's deep learning model
                    # Hardcoded - provides best audio quality
                    "type": "azure_deep_noise_suppression"
                },
                
                # ───────────────────────────────────────────────────
                # Avatar visual appearance
                # ───────────────────────────────────────────────────
                "avatar": {
                    # Character appearance (e.g., "jeff", "lisa")
                    # config["azure_avatar_character"] = os.getenv("AZURE_AVATAR_CHARACTER", "jeff")
                    "character": config["azure_avatar_character"],
                    
                    # Style/clothing (e.g., "business", "casual")
                    # config["azure_avatar_style"] = os.getenv("AZURE_AVATAR_STYLE", "business")
                    "style": config["azure_avatar_style"]
                },
                
                # ───────────────────────────────────────────────────
                # Voice selection for text-to-speech
                # ───────────────────────────────────────────────────
                "voice": {
                    # Neural voice name (e.g., "en-US-AndrewMultilingualNeural")
                    # config["azure_voice_name"] = os.getenv("AZURE_VOICE_NAME", "en-US-AndrewMultilingualNeural")
                    "name": config["azure_voice_name"],
                    
                    # Voice type: "azure-standard" for Azure neural voices
                    # Hardcoded - standard option for Azure voices
                    "type": "azure-standard"
                }
            }
        }
        
        # ═══════════════════════════════════════════════════════════
        # Step 3: Add agent-specific settings (local agents only)
        # ═══════════════════════════════════════════════════════════
        
        # Only add these if using local agent (not Azure AI agent)
        # Azure AI agents get their config from Azure portal, not here
        if agent_config and not agent_config.get("is_azure_agent"):
            # Add system instructions (AI personality)
            # agent_config["instructions"] comes from YAML file
            # Example: "You are a helpful customer service representative..."
            config_message["session"]["instructions"] = agent_config["instructions"]
            
            # Add temperature (creativity level: 0.0-1.0)
            # agent_config["temperature"] comes from YAML file
            # Example: 0.7
            config_message["session"]["temperature"] = agent_config["temperature"]
            
            # Add max response length
            # agent_config["max_tokens"] comes from YAML file
            # Example: 1000
            config_message["session"]["max_response_output_tokens"] = agent_config["max_tokens"]
        
        # ═══════════════════════════════════════════════════════════
        # Step 4: Send configuration to Azure as JSON
        # ═══════════════════════════════════════════════════════════
        await azure_ws.send(json.dumps(config_message))
    
    async def _forward_messages(self, client_ws, azure_ws):
        """
        Forward messages bidirectionally between client and Azure.
        
        Creates two tasks that run in parallel:
        1. Client → Azure
        2. Azure → Client
        """
        # Create two concurrent tasks
        tasks = [
            asyncio.create_task(self._client_to_azure(client_ws, azure_ws)),
            asyncio.create_task(self._azure_to_client(azure_ws, client_ws))
        ]
        
        # Wait until one completes (connection closed)
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        
        # Cancel the other task
        for task in pending:
            task.cancel()
    
    async def _client_to_azure(self, client_ws, azure_ws):
        """
        Forward messages from client to Azure.
        
        This runs continuously, receiving messages from the web client
        and sending them to Azure. Stops when connection closes.
        
        Uses executor pattern because Flask-Sock is synchronous but
        we need async for Azure WebSocket.
        
        Args:
            client_ws: Flask-Sock WebSocket (synchronous)
            azure_ws: Azure WebSocket (asynchronous)
        """
        try:
            # ═══════════════════════════════════════════════════════════
            # Loop continuously until connection closes
            # ═══════════════════════════════════════════════════════════
            while True:
                # ───────────────────────────────────────────────────
                # Receive from client using executor pattern
                # ───────────────────────────────────────────────────
                
                # Problem: client_ws.receive() is blocking (freezes code)
                # Solution: Run it in executor (background thread)
                
                # asyncio.get_event_loop() = get Python's async loop
                # .run_in_executor(None, client_ws.receive) = run blocking code
                # None = use default thread pool
                # client_ws.receive = function to run in background
                # await = wait for result without blocking other code
                message = await asyncio.get_event_loop().run_in_executor(
                    None, client_ws.receive
                )
                
                # ───────────────────────────────────────────────────
                # Check if connection closed
                # ───────────────────────────────────────────────────
                if message is None:
                    break  # Client disconnected
                
                # ───────────────────────────────────────────────────
                # Forward to Azure (async, no executor needed)
                # ───────────────────────────────────────────────────
                # await azure_ws.send(message) = send and wait
                # Azure WebSocket is already async-compatible
                await azure_ws.send(message)
        
        except Exception:
            pass  # Connection closed or error (normal)
    
    async def _azure_to_client(self, azure_ws, client_ws):
        """
        Forward messages from Azure to client.
        
        This runs continuously, receiving messages from Azure
        (AI responses, audio, events) and sending them to client.
        Stops when connection closes.
        
        Uses executor pattern for client sends because Flask-Sock
        is synchronous.
        
        Args:
            azure_ws: Azure WebSocket (asynchronous)
            client_ws: Flask-Sock WebSocket (synchronous)
        """
        try:
            # ═══════════════════════════════════════════════════════════
            # Loop through Azure messages (async iterator)
            # ═══════════════════════════════════════════════════════════
            
            # async for = wait for each message from Azure
            # azure_ws is async-compatible, so this works directly
            async for message in azure_ws:
                # ───────────────────────────────────────────────────
                # Send to client using executor pattern
                # ───────────────────────────────────────────────────
                
                # Problem: client_ws.send() is blocking (freezes code)
                # Solution: Run it in executor (background thread)
                
                # asyncio.get_event_loop() = get Python's async loop
                # .run_in_executor(None, client_ws.send, message):
                #   None = use default thread pool
                #   client_ws.send = function to call
                #   message = argument to pass to function
                # await = wait for send to complete
                await asyncio.get_event_loop().run_in_executor(
                    None, client_ws.send, message
                )
        
        except Exception:
            pass  # Connection closed or error (normal)
    
    async def _send_message(self, ws, message: Dict):
        """Send JSON message to WebSocket."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, ws.send, json.dumps(message)
            )
        except Exception:
            pass
    
    async def _send_error(self, ws, error_message: str):
        """Send error message to client."""
        await self._send_message(ws, {
            "type": "error",
            "error": {"message": error_message}
        })
```

**🎓 Teaching Points:**
1. **WebSocket Proxy Pattern:** Your server sits between client and Azure
2. **Async/Await:** Handle multiple connections concurrently
3. **Bidirectional Communication:** Messages flow both ways simultaneously
4. **Error Handling:** Always cleanup connections in `finally` block
5. **Authentication:** Azure needs API key in headers
6. **Session Configuration:** Tell Azure what voice, avatar, settings to use

**Why This Architecture?**
- ✅ **Security:** Client never sees Azure credentials
- ✅ **Flexibility:** Can modify/log messages in transit
- ✅ **Control:** Manage multiple agents with different configs

---

### **STEP 6: Flask Application** (20 minutes)

**File:** `backend/src/app.py`

**Purpose:** Create HTTP API endpoints and WebSocket endpoint.

**Complete Code:**

```python
# ═══════════════════════════════════════════════════════════════════
# Import statements
# ═══════════════════════════════════════════════════════════════════

import asyncio  # For running async code in sync context
import logging  # For server logging
from flask import Flask, jsonify, request  # Flask web framework
from flask_sock import Sock  # WebSocket support for Flask
from typing import Dict, Any, cast  # Type hints for better code clarity

# Import our custom modules
from src.config import config  # Config singleton (loads .env)
from src.services.managers import AgentManager, ScenarioManager  # Our managers
from src.services.websocket_handler import VoiceProxyHandler  # WebSocket handler

# ═══════════════════════════════════════════════════════════════════
# Configure logging (prints info to console)
# ═══════════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Create logger for this module

# ═══════════════════════════════════════════════════════════════════
# Initialize Flask app
# ═══════════════════════════════════════════════════════════════════

# Flask(__name__) = create Flask web server
# static_folder="../static" = serve files from ../static directory
# Hardcoded path - relative to app.py location
app = Flask(__name__, static_folder="../static")

# Sock(app) = add WebSocket support to Flask
# This allows /ws/voice endpoint to work
sock = Sock(app)

# ═══════════════════════════════════════════════════════════════════
# Initialize managers (global instances shared by all requests)
# ═══════════════════════════════════════════════════════════════════

# ScenarioManager() = loads all YAML scenarios from data/scenarios/
# Called once at startup, scenarios cached in memory
scenario_manager = ScenarioManager()

# AgentManager() = manages dynamically created agents
# Stores agent configs in memory dictionary
agent_manager = AgentManager()

# VoiceProxyHandler(agent_manager) = handles WebSocket connections
# Needs agent_manager to look up agent configurations
voice_proxy_handler = VoiceProxyHandler(agent_manager)


# ═══════════════════════════════════════════════════════════════════
# REST API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """
    Root endpoint - health check.
    
    Browser visit: http://localhost:5000/
    Returns: HTML string
    
    Used to verify server is running.
    """
    return "Voice Agent Backend Running! 🎉"


@app.route("/api/config")
def get_config():
    """
    Get client configuration.
    
    Client calls: GET /api/config
    Returns: JSON with WebSocket endpoint info
    
    This tells the frontend:
    - proxy_enabled: true = use backend as proxy
    - ws_endpoint: where to connect WebSocket
    """
    return jsonify({
        "proxy_enabled": True,  # Hardcoded - we always use proxy
        "ws_endpoint": "/ws/voice"  # Hardcoded - our WebSocket endpoint
    })


@app.route("/api/scenarios")
def get_scenarios():
    """
    List all available scenarios.
    
    Client calls: GET /api/scenarios
    Returns: JSON array like:
      [
        {
          "id": "customer-service",
          "name": "Customer Service Rep",
          "description": "Helpful assistant"
        }
      ]
    
    Uses scenario_manager to get cached scenarios.
    """
    # scenario_manager.list_scenarios() = get all scenarios
    # Returns list of dictionaries from YAML files
    # jsonify() = convert Python list to JSON response
    return jsonify(scenario_manager.list_scenarios())


@app.route("/api/scenarios/<scenario_id>")
def get_scenario(scenario_id: str):
    """
    Get a specific scenario by ID.
    
    Client calls: GET /api/scenarios/customer-service
    Args:
        scenario_id: Extracted from URL path (after /api/scenarios/)
                     Example: "customer-service"
    
    Returns: 
        - 200 JSON with scenario details if found
        - 404 JSON error if not found
    """
    # scenario_manager.get_scenario(scenario_id) = lookup scenario
    # Returns dictionary if found, None if not found
    scenario = scenario_manager.get_scenario(scenario_id)
    
    # Check if scenario exists
    if scenario:
        # jsonify(scenario) = convert dictionary to JSON response
        return jsonify(scenario)
    
    # Scenario not found
    # Return error message with 404 status code
    return jsonify({"error": "Scenario not found"}), 404


@app.route("/api/agents/create", methods=["POST"])
def create_agent():
    """
    Create a new agent for a scenario.
    
    Client calls: POST /api/agents/create
    Client sends JSON: {"scenario_id": "customer-service"}
    
    Returns:
        - 200 JSON with agent_id if successful
        - 400 error if scenario_id missing
        - 500 error if creation fails
    """
    # ───────────────────────────────────────────────────────────────
    # Step 1: Get request data
    # ───────────────────────────────────────────────────────────────
    
    # request.json = Flask gives us the JSON body as dictionary
    # cast(Dict[str, Any], ...) = tell TypeScript this is a dictionary
    # This is just for type hints, doesn't change behavior
    data = cast(Dict[str, Any], request.json)
    
    # data.get("scenario_id") = get scenario_id from JSON
    # Returns None if key doesn't exist (safe)
    scenario_id = data.get("scenario_id")
    
    # ───────────────────────────────────────────────────────────────
    # Step 2: Validate input
    # ───────────────────────────────────────────────────────────────
    
    if not scenario_id:
        # Return error with 400 Bad Request status
        return jsonify({"error": "scenario_id is required"}), 400
    
    # ───────────────────────────────────────────────────────────────
    # Step 3: Create agent
    # ───────────────────────────────────────────────────────────────
    
    # agent_manager.create_agent(scenario_id, scenario_manager)
    # Returns UUID string if successful, None if failed
    agent_id = agent_manager.create_agent(scenario_id, scenario_manager)
    
    # ───────────────────────────────────────────────────────────────
    # Step 4: Return result
    # ───────────────────────────────────────────────────────────────
    
    if agent_id:
        # Success - return agent info
        return jsonify({
            "agent_id": agent_id,  # UUID like "a1b2c3d4..."
            "scenario_id": scenario_id  # Echo back the scenario
        })
    
    # Failed to create agent
    return jsonify({"error": "Failed to create agent"}), 500


# ═══════════════════════════════════════════════════════════════════
# WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════════════════════════

@sock.route("/ws/voice")
def websocket_voice(ws):
    """
    WebSocket endpoint for voice connections.
    
    Client connects: ws://localhost:5000/ws/voice
    This is where real-time voice chat happens.
    
    Args:
        ws: Flask-Sock WebSocket object (synchronous)
    
    Flow:
        1. Client connects to /ws/voice
        2. This function is called with ws object
        3. VoiceProxyHandler manages Azure connection
        4. Messages flow: Client ↔ Backend ↔ Azure
    """
    logger.info("New WebSocket connection")
    
    # ───────────────────────────────────────────────────────────────
    # Bridge sync Flask to async handler
    # ───────────────────────────────────────────────────────────────
    
    # Problem: voice_proxy_handler.handle_connection() is async
    # Problem: Flask WebSocket endpoint is sync
    # Solution: asyncio.run() runs async code in sync context
    
    # asyncio.run(coroutine) = run async function until complete
    # voice_proxy_handler.handle_connection(ws) = async function
    # ws = Flask-Sock WebSocket (passed to handler)
    asyncio.run(voice_proxy_handler.handle_connection(ws))


# ═══════════════════════════════════════════════════════════════════
# SERVER STARTUP
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # This runs if you execute: python app.py
    
    # Get configuration from Config singleton
    # config["port"] = os.getenv("PORT", 5000) from .env
    # config["host"] = os.getenv("HOST", "0.0.0.0") from .env
    port = config["port"]
    host = config["host"]
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Start Flask web server
    # host = "0.0.0.0" means accept connections from any IP
    # port = 5000 (or from .env)
    # debug=True = auto-reload on code changes, show detailed errors
    app.run(host=host, port=port, debug=True)
```

**🎓 Teaching Points:**
1. **REST API Endpoints:** HTTP endpoints for configuration and agent creation
2. **WebSocket Endpoint:** Special endpoint for real-time communication
3. **Global Managers:** Shared instances across all requests
4. **Flask-Sock:** Bridges sync Flask with async WebSocket handling
5. **Error Responses:** Use proper HTTP status codes (400, 404, 500)

**API Endpoints Summary:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/api/config` | GET | Get client configuration |
| `/api/scenarios` | GET | List all scenarios |
| `/api/scenarios/<id>` | GET | Get specific scenario |
| `/api/agents/create` | POST | Create new agent |
| `/ws/voice` | WebSocket | Voice connection |

---

### **STEP 7: Running the Backend** (5 minutes)

Create `run.py` in root folder:

```python
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from src.app import app, config

if __name__ == "__main__":
    app.run(
        host=config["host"],
        port=config["port"],
        debug=True
    )
```

**Run the server:**
```bash
python run.py
```

**You should see:**
```
 * Running on http://0.0.0.0:8000
Starting server on 0.0.0.0:8000
```

---

## Frontend Implementation

### Overview

The frontend handles three critical responsibilities:
1. **Audio Capture** - Capture microphone audio using browser APIs
2. **Audio Processing** - Convert audio format for Azure compatibility
3. **Real-time Communication** - Maintain WebSocket connection with backend

**Tech Stack:**
- React + TypeScript
- Vite (build tool)
- Browser APIs: AudioContext, AudioWorklet, WebSocket

---

### **Key Concept 1: Audio Capture Pipeline**

**The Challenge:**
Browsers capture audio as **Float32Array** (values -1.0 to 1.0), but Azure expects **Int16 PCM Base64** format.

**The Solution - Three-Step Conversion:**

```
Microphone → Float32 → Int16 → Base64 → JSON → WebSocket
            (browser)  (convert) (encode) (wrap)  (send)
```

**File:** `frontend/src/hooks/useRecorder.ts`

```typescript
// STEP 1: Create AudioContext at 24kHz (Azure's sample rate)
const audioContext = new AudioContext({ sampleRate: 24000 });

// STEP 2: Access user's microphone
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const source = audioContext.createMediaStreamSource(stream);

// STEP 3: Create AudioWorklet for low-latency processing
await audioContext.audioWorklet.addModule('/audio-processor.js');
const workletNode = new AudioWorkletNode(audioContext, 'audio-processor');

// STEP 4: Connect pipeline
source.connect(workletNode).connect(audioContext.destination);

// STEP 5: Receive audio chunks from worklet
workletNode.port.onmessage = (event) => {
  const float32Audio = event.data; // Float32Array from AudioWorklet
  
  // Convert Float32 (-1.0 to 1.0) → Int16 (-32768 to 32767)
  const int16Array = new Int16Array(float32Audio.length);
  for (let i = 0; i < float32Audio.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Audio[i])); // Clamp to [-1, 1]
    int16Array[i] = s < 0 ? s * 32768 : s * 32767;         // Scale to Int16
  }
  
  // Convert Int16 binary → Base64 string
  const uint8Array = new Uint8Array(int16Array.buffer);
  const base64 = btoa(String.fromCharCode(...uint8Array));
  
  // Send to callback (will be sent to backend)
  onAudioChunk(base64);
};
```

**🎯 Key Teaching Points:**
- **AudioContext** manages all audio operations
- **24kHz sample rate** matches Azure's requirements
- **AudioWorklet** runs in separate thread for performance
- **Float32 → Int16** conversion preserves audio quality
- **Base64 encoding** allows binary data in JSON messages

---

### **Key Concept 2: WebSocket Communication**

**File:** `frontend/src/hooks/useRealtime.ts`

```typescript
const useRealtime = () => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  // Connect to backend WebSocket endpoint
  const connect = () => {
    const websocket = new WebSocket('ws://localhost:8000/ws/voice');
    
    websocket.onopen = () => {
      console.log('Connected to backend');
    };
    
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      // Route messages based on type
      switch (message.type) {
        case 'response.audio.delta':
          // Azure sent audio chunk - play it
          playAudioChunk(message.delta);
          break;
        
        case 'conversation.item.input_audio_transcription.completed':
          // User's speech was transcribed
          setUserTranscript(message.transcript);
          break;
        
        case 'response.done':
          // AI finished speaking
          setAgentStatus('idle');
          break;
      }
    };
    
    setWs(websocket);
  };
  
  // Send audio to backend
  const sendAudioChunk = (base64Audio: string) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'input_audio_buffer.append',
        audio: base64Audio
      }));
    }
  };
  
  return { connect, sendAudioChunk };
};
```

**🎯 Key Teaching Points:**
- **WebSocket** provides full-duplex (two-way) communication
- **Message routing** based on `type` field
- **Stateful connection** - check `readyState` before sending
- **JSON protocol** - all messages are JSON strings

---

### **Key Concept 3: Connecting the Pieces**

**File:** `frontend/src/app/App.tsx`

```typescript
const App = () => {
  // Initialize hooks
  const { connect, sendAudioChunk } = useRealtime();
  const { startRecording, stopRecording } = useRecorder({
    onAudioChunk: (base64) => {
      // This callback fires every time AudioWorklet captures audio
      sendAudioChunk(base64); // Send to backend immediately
    }
  });
  
  const handleStartCall = async () => {
    // 1. Establish WebSocket connection
    await connect();
    
    // 2. Wait for connection (you'd use a promise/state here)
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 3. Start capturing microphone
    await startRecording();
    
    // 4. Audio chunks now flow automatically:
    //    Microphone → useRecorder → onAudioChunk → sendAudioChunk → WebSocket
  };
  
  return (
    <button onClick={handleStartCall}>
      Start Voice Call
    </button>
  );
};
```

**🎯 Key Teaching Points:**
- **Hook composition** - combine multiple hooks for complex behavior
- **Callback pattern** - `onAudioChunk` connects recorder to WebSocket
- **Async initialization** - WebSocket must connect before sending audio
- **Automatic streaming** - once started, audio flows continuously

---

### **Complete Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER (React)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Microphone (24kHz)                                           │
│      ↓                                                           │
│  2. AudioWorklet (separate thread)                               │
│      ↓                                                           │
│  3. Float32Array [-1.0 to 1.0]                                   │
│      ↓                                                           │
│  4. Convert to Int16 [-32768 to 32767]      ← useRecorder.ts    │
│      ↓                                                           │
│  5. Encode to Base64 string                                      │
│      ↓                                                           │
│  6. Wrap in JSON:                                                │
│     {type: "input_audio_buffer.append", audio: "base64..."}      │
│      ↓                                                           │
│  7. WebSocket.send()                         ← useRealtime.ts   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask + Python)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  8. Receive JSON message                                         │
│      ↓                                                           │
│  9. Forward to Azure (no modification)      ← websocket_handler  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      AZURE AI FOUNDRY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  10. Decode Base64 → PCM audio                                   │
│       ↓                                                          │
│  11. Speech-to-Text (Whisper model)                              │
│       ↓                                                          │
│  12. Process with GPT-4o                                         │
│       ↓                                                          │
│  13. Text-to-Speech                                              │
│       ↓                                                          │
│  14. Encode as Base64                                            │
│       ↓                                                          │
│  15. Send back: {type: "response.audio.delta", delta: "..."}     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND (Flask)                          │
│  16. Forward to browser (no modification)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓ WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER (React)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  17. Parse JSON message                      ← useRealtime.ts   │
│       ↓                                                          │
│  18. Decode Base64 → Int16 PCM                                   │
│       ↓                                                          │
│  19. Play through speakers                   ← useAudioPlayer.ts │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### **Essential Frontend Files Summary**

| File | Purpose | Key Functions |
|------|---------|---------------|
| `useRecorder.ts` | Audio capture & conversion | Float32→Int16→Base64 conversion |
| `useRealtime.ts` | WebSocket management | connect(), send(), message routing |
| `useAudioPlayer.ts` | Play Azure's audio responses | Base64→PCM→AudioContext playback |
| `App.tsx` | Main component | Connects all hooks together |

---

### **Frontend Setup Commands**

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Key dependencies in package.json:
# - react: UI framework
# - typescript: Type safety
# - vite: Fast build tool

# Start development server
npm run dev

# Build for production
npm run build
```

---

### **Critical Browser APIs Used**

1. **AudioContext** - Main audio processing interface
   - Sample rate control (24kHz)
   - Audio node graph management

2. **AudioWorklet** - Low-latency audio processing
   - Runs in separate thread
   - Prevents UI blocking
   - Real-time audio chunk delivery

3. **getUserMedia** - Microphone access
   - Requests user permission
   - Returns MediaStream

4. **WebSocket** - Full-duplex communication
   - Persistent connection
   - Low latency (~10-50ms)
   - Bidirectional message flow

---

### **Why This Architecture?**

**Frontend Handles Audio Processing Because:**
- Browser has direct microphone access
- AudioWorklet provides low-latency capture
- Reduces backend CPU load
- Backend can be stateless proxy

**WebSocket Instead of HTTP Because:**
- Voice requires real-time (~50ms latency)
- HTTP request/response too slow
- WebSocket maintains persistent connection
- Bidirectional - Azure can send audio anytime

**Base64 Encoding Because:**
- JSON doesn't support binary data
- WebSocket can send text or binary
- Text mode (JSON) is easier to debug
- Base64 overhead (~33%) acceptable for voice

---


