"""
Debug script to test Azure Voice API connection.
Run this to diagnose connection issues.
"""
import os
import sys
import asyncio
import websockets
from dotenv import load_dotenv

load_dotenv()

async def test_azure_connection():
    """Test connection to Azure Voice API."""
    
    # Get configuration
    resource_name = os.getenv("AZURE_AI_RESOURCE_NAME")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    agent_id = os.getenv("AGENT_ID")
    use_azure_agents = os.getenv("USE_AZURE_AI_AGENTS", "").lower() == "true"
    model_name = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    print("=" * 60)
    print("Azure Voice API Connection Test")
    print("=" * 60)
    print(f"Resource Name: {resource_name}")
    print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
    print(f"Agent ID: {agent_id}")
    print(f"Use Azure AI Agents: {use_azure_agents}")
    print(f"Model: {model_name}")
    print("=" * 60)
    
    if not resource_name:
        print("❌ ERROR: AZURE_AI_RESOURCE_NAME not set")
        return False
    
    if not api_key:
        print("❌ ERROR: AZURE_OPENAI_API_KEY not set")
        return False
    
    # Build URL
    if use_azure_agents:
        domain = "ai.azure.com"
        endpoint = "/voice/chat/v1"
        base_url = f"wss://{resource_name}.{domain}{endpoint}"
        
        if agent_id:
            azure_url = f"{base_url}?api-version=2025-10-01&agent-id={agent_id}"
        else:
            azure_url = f"{base_url}?api-version=2025-10-01&model={model_name}"
    else:
        domain = "cognitiveservices.azure.com"
        endpoint = "/openai/realtime"
        base_url = f"wss://{resource_name}.{domain}{endpoint}"
        azure_url = f"{base_url}?api-version=2024-12-01-preview&deployment={model_name}"
    
    print(f"\n🔗 Connection URL:")
    print(f"{azure_url}")
    print()
    
    # Test connection
    headers = {"api-key": api_key}
    
    try:
        print("🔌 Attempting to connect...")
        async with websockets.connect(azure_url, additional_headers=headers) as ws:
            print("✅ Connection successful!")
            
            # Try to send initial config
            config_message = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "turn_detection": {"type": "server_vad"},
                }
            }
            
            print("📤 Sending session configuration...")
            await ws.send(str(config_message))
            
            print("✅ Configuration sent successfully!")
            print("\n✅ All tests passed! Azure connection is working.")
            return True
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed with status code: {e.status_code}")
        print(f"   Response headers: {e.response_headers}")
        if e.status_code == 401:
            print("   → Check your AZURE_OPENAI_API_KEY")
        elif e.status_code == 404:
            print("   → Check your AZURE_AI_RESOURCE_NAME and model/agent configuration")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_azure_connection())
    sys.exit(0 if success else 1)
