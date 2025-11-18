# ---------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
# --------------------------------------------------------------------------------------------

"""WebSocket handling for voice proxy connections."""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional

import simple_websocket.ws  # pyright: ignore[reportMissingTypeStubs]
import websockets
import websockets.asyncio.client

from src.config import config
from src.services.managers import AgentManager

logger = logging.getLogger(__name__)

# WebSocket constants
# API version for Azure Voice services - defines which features/endpoints are available
AZURE_VOICE_API_VERSION = "2025-10-01"
# Base domain for Azure Cognitive Services endpoints (traditional Azure OpenAI service)
AZURE_COGNITIVE_SERVICES_DOMAIN = "cognitiveservices.azure.com"
# Base domain for Azure AI Foundry services (newer Azure AI agents platform)
AZURE_AI_FOUNDRY_DOMAIN = "services.ai.azure.com"
# Endpoint path for voice agent functionality on Cognitive Services
VOICE_AGENT_ENDPOINT = "voice-agent/realtime"
# Endpoint path for voice functionality on AI Foundry
AI_FOUNDRY_VOICE_ENDPOINT = "voice-live/realtime"

# Session configuration constants
# Default modalities supported in the voice session (text and audio I/O)
DEFAULT_MODALITIES = ["text", "audio"]
# Voice Activity Detection (VAD) type - Azure's semantic VAD understands speech context
DEFAULT_TURN_DETECTION_TYPE = "azure_semantic_vad"
# Audio preprocessing - Azure's deep learning-based noise suppression
DEFAULT_NOISE_REDUCTION_TYPE = "azure_deep_noise_suppression"
# Echo cancellation handled server-side to prevent audio feedback loops
DEFAULT_ECHO_CANCELLATION_TYPE = "server_echo_cancellation"
# Default avatar character for visual representation
DEFAULT_AVATAR_CHARACTER = "jeff"
# Default avatar style/appearance
DEFAULT_AVATAR_STYLE = "business"
# Default neural voice for text-to-speech output
DEFAULT_VOICE_NAME = "en-US-AndrewMultilingualNeural"
# Voice type - standard Azure neural voices
DEFAULT_VOICE_TYPE = "azure-standard"

# Message types
# Message type for updating session configuration
SESSION_UPDATE_TYPE = "session.update"
# Custom message type to notify client of successful proxy connection
PROXY_CONNECTED_TYPE = "proxy.connected"
# Message type for error notifications
ERROR_TYPE = "error"

# Log message truncation length
# Maximum characters to log from messages (prevents log bloat with large payloads)
LOG_MESSAGE_MAX_LENGTH = 100


class VoiceProxyHandler:
    """
    Handles WebSocket proxy connections between client and Azure Voice API.
    
    This class acts as a transparent proxy, forwarding messages bidirectionally
    between a client WebSocket connection and Azure's Voice API. It handles:
    - Agent configuration management
    - Azure connection establishment with proper authentication
    - Session initialization with audio/voice settings
    - Bidirectional message forwarding
    """

    def __init__(self, agent_manager: AgentManager):
        """
        Initialize the voice proxy handler.

        Args:
            agent_manager: Agent manager instance that handles agent configurations
                          and provides access to agent-specific settings
        """
        self.agent_manager = agent_manager

    async def handle_connection(self, client_ws: simple_websocket.ws.Server) -> None:
        """
        Handle a WebSocket connection from a client.
        
        Main entry point for processing a client connection. Orchestrates:
        1. Extracting agent ID from initial client message
        2. Establishing connection to Azure Voice API
        3. Notifying client of successful proxy connection
        4. Managing bidirectional message forwarding
        5. Cleanup on connection closure

        Args:
            client_ws: The client WebSocket connection (from Flask-SocketIO)
        """

        azure_ws = None
        current_agent_id = None

        try:
            # Extract agent ID from the first message sent by client
            current_agent_id = await self._get_agent_id_from_client(client_ws)

            # Establish connection to Azure with agent-specific configuration
            azure_ws = await self._connect_to_azure(current_agent_id)
            if not azure_ws:
                await self._send_error(client_ws, "Failed to connect to Azure Voice API")
                return

            # Notify client that proxy connection is established
            await self._send_message(
                client_ws,
                {"type": "proxy.connected", "message": "Connected to Azure Voice API"},
            )

            # Start forwarding messages bidirectionally until connection closes
            await self._handle_message_forwarding(client_ws, azure_ws)

        except Exception as e:
            logger.error("Proxy error: %s", e)
            await self._send_error(client_ws, str(e))

        finally:
            # Always cleanup Azure connection on exit
            if azure_ws:
                await azure_ws.close()

    async def _get_agent_id_from_client(self, client_ws: simple_websocket.ws.Server) -> Optional[str]:
        """
        Get agent ID from initial client message or use pre-configured agent.
        
        MOBILE BACKEND MODE:
        - If AGENT_ID is set in environment (Azure AI Foundry agent), use that directly
        - Otherwise, auto-create an agent with NBK banking scenario
        - No longer requires client to send initial session.update message
        
        LEGACY MODE (for backwards compatibility):
        - Still accepts session.update message with agent_id from client
        
        Args:
            client_ws: Client WebSocket connection
            
        Returns:
            Agent ID string (from env, auto-created, or client message)
        """
        from src.config import DEFAULT_SCENARIO_ID
        
        # MOBILE BACKEND MODE: Check if AGENT_ID is pre-configured in environment
        # This is set via Azure Container App environment variable after deploying
        env_agent_id = config.get("agent_id")
        if env_agent_id and config.get("use_azure_ai_agents"):
            logger.info("Using pre-configured Azure AI Foundry agent: %s", env_agent_id)
            return env_agent_id
        
        # MOBILE BACKEND MODE: Auto-create agent with NBK scenario if no env agent configured
        if not env_agent_id:
            logger.info("No pre-configured agent found. Auto-creating agent with NBK banking scenario...")
            scenario = self.agent_manager.get_scenario_manager().get_scenario(DEFAULT_SCENARIO_ID)
            if scenario:
                agent_id = self.agent_manager.create_agent(DEFAULT_SCENARIO_ID, scenario)
                logger.info("Auto-created agent: %s for scenario: %s", agent_id, DEFAULT_SCENARIO_ID)
                return agent_id
            else:
                logger.error("Failed to load NBK scenario: %s", DEFAULT_SCENARIO_ID)
                return None
        
        # LEGACY MODE: Try to receive agent_id from client message (backwards compatibility)
        try:
            # Receive first message synchronously in executor (simple_websocket is sync)
            first_message: str | None = await asyncio.get_event_loop().run_in_executor(
                None,
                client_ws.receive,  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
            )
            if first_message:
                msg = json.loads(first_message)
                # Check for session.update message with agent_id
                if msg.get("type") == "session.update":
                    return msg.get("session", {}).get("agent_id")
        except Exception as e:
            logger.error("Error getting agent ID from client: %s", e)
            
        return None

    async def _connect_to_azure(self, agent_id: Optional[str]) -> Optional[websockets.asyncio.client.ClientConnection]:
        """
        Connect to Azure Voice API with appropriate configuration.
        
        Establishes WebSocket connection to Azure, handling:
        - URL construction based on agent type (Azure AI agent vs OpenAI model)
        - API key authentication
        - Initial session configuration
        
        Args:
            agent_id: Optional agent ID to use specific agent configuration
            
        Returns:
            Connected WebSocket client or None if connection fails
        """
        try:
            # Retrieve agent configuration if agent_id provided
            agent_config = self.agent_manager.get_agent(agent_id) if agent_id else None

            # Build appropriate Azure WebSocket URL based on agent type
            azure_url = self._build_azure_url(agent_id, agent_config)

            # Get API key from configuration
            api_key = config.get("azure_openai_api_key")
            if not api_key:
                logger.error("No API key found in configuration (azure_openai_api_key)")
                return None

            # Set authentication header
            headers = {"api-key": api_key}

            # Establish WebSocket connection to Azure
            azure_ws = await websockets.connect(azure_url, additional_headers=headers)
            logger.info("Connected to Azure Voice API with agent: %s", agent_id or "default")

            # Send initial session configuration to Azure
            await self._send_initial_config(azure_ws, agent_config)

            return azure_ws

        except Exception as e:
            logger.error("Failed to connect to Azure: %s", e)
            return None

    def _build_azure_url(self, agent_id: Optional[str], agent_config: Optional[Dict[str, Any]]) -> str:
        """
        Build the Azure WebSocket URL.
        
        Constructs the appropriate URL based on:
        - Whether using Azure AI agents or direct OpenAI models
        - Whether agent configuration exists
        - Fallback to default configuration
        
        Args:
            agent_id: Optional agent identifier
            agent_config: Optional agent configuration dictionary
            
        Returns:
            Complete WebSocket URL for Azure connection
        """
        # Build base URL (includes domain, endpoint, api-version)
        base_url = self._build_base_azure_url()

        # If agent config exists, use agent-specific URL construction
        if agent_config:
            return self._build_agent_specific_url(base_url, agent_id, agent_config)
        # If global agent_id configured, use that
        if config["agent_id"]:
            return f"{base_url}&agent-id={config['agent_id']}"
        # Fallback to model name from configuration
        model_name = config["model_deployment_name"]
        return f"{base_url}&model={model_name}"

    def _build_base_azure_url(self) -> str:
        """
        Build the base Azure WebSocket URL.
        
        Constructs the protocol, domain, endpoint path, and standard query parameters.
        Chooses between AI Foundry and Cognitive Services domains based on configuration.
        
        Returns:
            Base WebSocket URL without model/agent-specific parameters
        """
        resource_name = config["azure_ai_resource_name"]
        # Generate unique client request ID for tracing/debugging
        client_request_id = uuid.uuid4()

        # Use AI Foundry domain if using Azure AI agents
        if config.get("use_azure_ai_agents"):
            domain = AZURE_AI_FOUNDRY_DOMAIN
            endpoint = AI_FOUNDRY_VOICE_ENDPOINT
            return (
                f"wss://{resource_name}.{domain}/"
                f"{endpoint}?api-version={AZURE_VOICE_API_VERSION}"
                f"&x-ms-client-request-id={client_request_id}"
            )

        # Default to Cognitive Services domain for direct OpenAI models
        return (
            f"wss://{resource_name}.{AZURE_COGNITIVE_SERVICES_DOMAIN}/"
            f"{VOICE_AGENT_ENDPOINT}?api-version={AZURE_VOICE_API_VERSION}"
            f"&x-ms-client-request-id={client_request_id}"
        )

    def _build_agent_specific_url(self, base_url: str, agent_id: Optional[str], agent_config: Dict[str, Any]) -> str:
        """
        Build URL for specific agent configuration.
        
        Differentiates between:
        - Azure AI agents: requires agent-id and project-id parameters
        - Local agents: uses model parameter with specific deployment
        
        Args:
            base_url: Base URL with protocol, domain, endpoint
            agent_id: Agent identifier
            agent_config: Agent configuration containing agent type and settings
            
        Returns:
            Complete URL with agent-specific parameters
        """
        if agent_config.get("is_azure_agent"):
            # For Azure AI agents, add agent-id and project-id
            project_name = config["azure_ai_project_name"]
            return f"{base_url}&agent-id={agent_id}&project-id={project_name}"
        # For local agents, use the model parameter
        model_name = agent_config.get("model", config["model_deployment_name"])
        return f"{base_url}&model={model_name}"

    async def _send_initial_config(
        self,
        azure_ws: websockets.asyncio.client.ClientConnection,
        agent_config: Optional[Dict[str, Any]],
    ) -> None:
        """
        Send initial configuration to Azure.
        
        Configures the Azure session with:
        - Audio settings (VAD, noise reduction, echo cancellation)
        - Voice and avatar settings
        - Transcription settings
        - Agent-specific instructions and parameters (for local agents)
        
        Args:
            azure_ws: Connected Azure WebSocket client
            agent_config: Optional agent configuration to apply
        """
        # Build base session configuration with audio/voice settings
        config_message = self._build_session_config()

        # Add agent-specific settings for local (non-Azure) agents
        # Azure AI agents get their config from the Azure platform directly
        if agent_config and not agent_config.get("is_azure_agent"):
            self._add_local_agent_config(config_message, agent_config)

        # Send configuration as JSON to Azure
        await azure_ws.send(json.dumps(config_message))

    def _build_session_config(self) -> Dict[str, Any]:
        """
        Build the base session configuration.
        
        Creates standard session settings including:
        - Modalities (text/audio)
        - Turn detection (VAD configuration)
        - Audio preprocessing (noise reduction, echo cancellation)
        - Transcription settings
        - Avatar appearance
        - Voice selection
        
        Returns:
            Session configuration dictionary
        """
        return {
            "type": SESSION_UPDATE_TYPE,
            "session": {
                # Enable both text and audio input/output
                "modalities": DEFAULT_MODALITIES,
                # Configure voice activity detection for turn-taking
                "turn_detection": {"type": DEFAULT_TURN_DETECTION_TYPE},
                # Configure input audio transcription (speech-to-text)
                "input_audio_transcription": {
                    "model": config["azure_input_transcription_model"],
                    "language": config["azure_input_transcription_language"],
                },
                # Enable noise reduction for clearer audio input
                "input_audio_noise_reduction": {"type": DEFAULT_NOISE_REDUCTION_TYPE},
                # Enable echo cancellation to prevent feedback
                "input_audio_echo_cancellation": {"type": DEFAULT_ECHO_CANCELLATION_TYPE},
                # Configure visual avatar appearance
                "avatar": {
                    "character": DEFAULT_AVATAR_CHARACTER,
                    "style": DEFAULT_AVATAR_STYLE,
                },
                # Configure text-to-speech voice
                "voice": {
                    "name": config["azure_voice_name"],
                    "type": config["azure_voice_type"],
                },
            },
        }

    def _add_local_agent_config(self, config_message: Dict[str, Any], agent_config: Dict[str, Any]) -> None:
        """
        Add local agent configuration to session config.
        
        Augments the session configuration with agent-specific settings:
        - Model deployment name
        - System instructions/prompt
        - Temperature (creativity/randomness)
        - Max output tokens (response length limit)
        
        Args:
            config_message: Base session configuration to modify
            agent_config: Agent-specific settings to apply
        """
        session = config_message["session"]
        # Specify which model deployment to use
        session["model"] = agent_config.get("model", config["model_deployment_name"])
        # Set system instructions for agent behavior
        session["instructions"] = agent_config["instructions"]
        # Set temperature for response creativity
        session["temperature"] = agent_config["temperature"]
        # Set maximum tokens for response length
        session["max_response_output_tokens"] = agent_config["max_tokens"]

    async def _handle_message_forwarding(
        self,
        client_ws: simple_websocket.ws.Server,
        azure_ws: websockets.asyncio.client.ClientConnection,
    ) -> None:
        """
        Handle bidirectional message forwarding.
        
        Creates two concurrent tasks to forward messages:
        1. Client -> Azure: forwards client messages to Azure
        2. Azure -> Client: forwards Azure responses to client
        
        Continues until either connection closes, then cancels the other task.
        
        Args:
            client_ws: Client WebSocket connection
            azure_ws: Azure WebSocket connection
        """
        # Create concurrent forwarding tasks
        tasks = [
            asyncio.create_task(self._forward_client_to_azure(client_ws, azure_ws)),
            asyncio.create_task(self._forward_azure_to_client(azure_ws, client_ws)),
        ]

        # Wait until one task completes (connection closed)
        _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel the remaining task to cleanup
        for task in pending:
            task.cancel()

    async def _forward_client_to_azure(
        self,
        client_ws: simple_websocket.ws.Server,
        azure_ws: websockets.asyncio.client.ClientConnection,
    ) -> None:
        """
        Forward messages from client to Azure.
        
        Continuously receives messages from client and sends them to Azure.
        Runs until client disconnects or an error occurs.
        
        Args:
            client_ws: Client WebSocket connection (synchronous library)
            azure_ws: Azure WebSocket connection (async library)
        """
        try:
            while True:
                # Receive message from client (sync call in executor)
                message: Optional[Any] = await asyncio.get_event_loop().run_in_executor(
                    None,
                    client_ws.receive,  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
                )
                # None indicates connection closed
                if message is None:
                    break
                # Log truncated message for debugging
                logger.debug("Client->Azure: %s", message[:LOG_MESSAGE_MAX_LENGTH])
                # Forward to Azure asynchronously
                await azure_ws.send(message)
        except Exception:
            # Connection closed gracefully
            logger.debug("Client connection closed during forwarding")

    async def _forward_azure_to_client(
        self,
        azure_ws: websockets.asyncio.client.ClientConnection,
        client_ws: simple_websocket.ws.Server,
    ) -> None:
        """
        Forward messages from Azure to client.
        
        Continuously receives messages from Azure and sends them to client.
        Runs until Azure disconnects or an error occurs.
        
        Args:
            azure_ws: Azure WebSocket connection (async library)
            client_ws: Client WebSocket connection (synchronous library)
        """
        try:
            # Iterate over incoming Azure messages asynchronously
            async for message in azure_ws:
                # Log truncated message for debugging
                logger.debug("Azure->Client: %s", message[:LOG_MESSAGE_MAX_LENGTH])
                # Send to client (sync call in executor)
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    client_ws.send,  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
                    message,
                )
        except Exception:
            # Connection closed gracefully
            logger.debug("Client connection closed during forwarding")

    async def _send_message(self, ws: simple_websocket.ws.Server, message: Dict[str, str | Dict[str, str]]) -> None:
        """
        Send a JSON message to a WebSocket.
        
        Helper method to send structured messages to client.
        Handles JSON serialization and async-to-sync conversion.
        
        Args:
            ws: WebSocket connection to send to
            message: Message dictionary to send as JSON
        """
        try:
            # Send JSON-encoded message in executor (sync call)
            await asyncio.get_event_loop().run_in_executor(
                None,
                ws.send,  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]
                json.dumps(message),
            )
        except Exception:
            # Silently fail if client already disconnected
            pass

    async def _send_error(self, ws: simple_websocket.ws.Server, error_message: str) -> None:
        """
        Send an error message to a WebSocket.
        
        Helper method to send standardized error messages to client.
        
        Args:
            ws: WebSocket connection to send error to
            error_message: Human-readable error description
        """
        await self._send_message(ws, {"type": "error", "error": {"message": error_message}})
