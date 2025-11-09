# ---------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Configuration management for the upskilling agent application."""

import os
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Default values as constants
# Server configuration defaults
DEFAULT_PORT = 8000  # Default port for the web server
DEFAULT_HOST = "0.0.0.0"  # Default host (binds to all network interfaces)

# Azure AI configuration defaults
DEFAULT_REGION = "swedencentral"  # Default Azure region for AI services
DEFAULT_MODEL = "gpt-4o"  # Default OpenAI model deployment name
DEFAULT_API_VERSION = "2024-12-01-preview"  # Azure OpenAI API version

# Speech and transcription defaults
DEFAULT_SPEECH_LANGUAGE = "ar-SA,en-US"  # Supported languages: Arabic (Saudi Arabia) and English (US)
DEFAULT_INPUT_TRANSCRIPTION_MODEL = "azure-speech"  # Speech-to-text model for input transcription
DEFAULT_INPUT_NOISE_REDUCTION_TYPE = "azure_deep_noise_suppression"  # Noise reduction algorithm for audio input

# Voice synthesis defaults
DEFAULT_VOICE_NAME = "en-US-AndrewMultilingualNeural"  # Azure Neural TTS voice
DEFAULT_VOICE_TYPE = "azure-standard"  # Voice synthesis type

# Avatar configuration defaults
DEFAULT_AVATAR_CHARACTER = "jeff"  # Default avatar character name
DEFAULT_AVATAR_STYLE = "business"  # Default avatar style/appearance


class Config:
    """Application configuration class.
    
    Manages all configuration settings for the upskilling agent application,
    loading values from environment variables with sensible defaults.
    """

    def __init__(self):
        """Initialize configuration from environment variables."""
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables with defaults.
        
        Returns:
            Dict[str, Any]: Dictionary containing all configuration settings
        """
        result: Dict[str, Any] = {
            # Azure AI Foundry project configuration
            "azure_ai_resource_name": os.getenv("AZURE_AI_RESOURCE_NAME", ""),  # Azure AI resource name
            "azure_ai_region": os.getenv("AZURE_AI_REGION", DEFAULT_REGION),  # Azure AI resource region
            "azure_ai_project_name": os.getenv("AZURE_AI_PROJECT_NAME", ""),  # Azure AI project name
            "project_endpoint": os.getenv("PROJECT_ENDPOINT", ""),  # Azure AI project endpoint URL
            
            # Azure AI Agents configuration
            "use_azure_ai_agents": self._parse_bool_env("USE_AZURE_AI_AGENTS"),  # Flag to enable Azure AI Agents
            "agent_id": os.getenv("AGENT_ID", ""),  # Specific agent ID if using Azure AI Agents
            
            # Server configuration
            "port": int(os.getenv("PORT", str(DEFAULT_PORT))),  # Port number for the web server
            "host": os.getenv("HOST", DEFAULT_HOST),  # Host address for the web server
            
            # Azure OpenAI configuration
            "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),  # Azure OpenAI service endpoint
            "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),  # Azure OpenAI API key
            "model_deployment_name": os.getenv("MODEL_DEPLOYMENT_NAME", DEFAULT_MODEL),  # OpenAI model deployment name
            "subscription_id": os.getenv("SUBSCRIPTION_ID", ""),  # Azure subscription ID
            "resource_group_name": os.getenv("RESOURCE_GROUP_NAME", ""),  # Azure resource group name
            
            # Azure Speech Services configuration
            "azure_speech_key": os.getenv("AZURE_SPEECH_KEY", ""),  # Azure Speech Services API key
            "azure_speech_region": os.getenv("AZURE_SPEECH_REGION", DEFAULT_REGION),  # Azure Speech Services region
            "azure_speech_language": os.getenv("AZURE_SPEECH_LANGUAGE", DEFAULT_SPEECH_LANGUAGE),  # Speech language(s)
            "api_version": DEFAULT_API_VERSION,  # Azure OpenAI API version
            
            # Input audio processing configuration
            "azure_input_transcription_model": os.getenv(
                "AZURE_INPUT_TRANSCRIPTION_MODEL", DEFAULT_INPUT_TRANSCRIPTION_MODEL
            ),  # Model used for transcribing user audio input
            "azure_input_transcription_language": os.getenv(
                "AZURE_INPUT_TRANSCRIPTION_LANGUAGE", DEFAULT_SPEECH_LANGUAGE
            ),  # Language(s) for input transcription
            "azure_input_noise_reduction_type": os.getenv(
                "AZURE_INPUT_NOISE_REDUCTION_TYPE", DEFAULT_INPUT_NOISE_REDUCTION_TYPE
            ),  # Noise reduction algorithm applied to input audio
            
            # Voice synthesis configuration
            "azure_voice_name": os.getenv("AZURE_VOICE_NAME", DEFAULT_VOICE_NAME),  # Azure Neural TTS voice name
            "azure_voice_type": os.getenv("AZURE_VOICE_TYPE", DEFAULT_VOICE_TYPE),  # Voice synthesis type/tier
            
            # Avatar configuration
            "azure_avatar_character": os.getenv("AZURE_AVATAR_CHARACTER", DEFAULT_AVATAR_CHARACTER),  # Avatar character
            "azure_avatar_style": os.getenv("AZURE_AVATAR_STYLE", DEFAULT_AVATAR_STYLE),  # Avatar style/appearance
            
            # Bing Grounding with Custom Search configuration
            "bing_grounding_resource_key": os.getenv("BING_GROUNDING_RESOURCE_KEY", ""),  # Bing Custom Search API key
            "bing_grounding_resource_name": os.getenv("BING_GROUNDING_RESOURCE_NAME", ""),  # Bing resource name
            "bing_grounding_config_id": os.getenv("BING_GROUNDING_CONFIG_ID", ""),  # Bing Custom Search config ID
        }
        return result

    def _parse_bool_env(self, env_var: str, default: bool = False) -> bool:
        """Parse boolean environment variable.
        
        Converts string environment variable values to boolean.
        Accepts "true" (case-insensitive) as True, everything else as False.
        
        Args:
            env_var: Name of the environment variable to parse
            default: Default value if environment variable is not set
            
        Returns:
            bool: Parsed boolean value
        """
        return os.getenv(env_var, str(default)).lower() == "true"

    def __getitem__(self, key: str) -> Any:
        """Get configuration value by key using dictionary-style access.
        
        Args:
            key: Configuration key to retrieve
            
        Returns:
            Any: Configuration value for the specified key
        """
        return self._config.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default.
        
        Args:
            key: Configuration key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            Any: Configuration value for the specified key, or default if not found
        """
        return self._config.get(key, default)

    @property
    def as_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary.
        
        Returns:
            Dict[str, Any]: Copy of the configuration dictionary
        """
        return self._config.copy()


# Global configuration instance
# Import and use this instance throughout the application to access configuration
config = Config()
