# ---------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Business logic managers for the upskilling agent application."""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from src.config import config
from src.services.graph_scenario_generator import GraphScenarioGenerator
from src.services.scenario_utils import determine_scenario_directory

# Constants
ROLE_PLAY_FILE_SUFFIX = "-role-play.prompt.yml"  # File naming convention for scenario files
ROLE_PLAY_SUFFIX_REMOVAL = "-role-play.prompt"  # Suffix to remove when extracting scenario ID
AGENT_ID_PREFIX = "local-agent"  # Prefix for locally created agents
AZURE_AGENT_NAME_PREFIX = "agent"  # Prefix for Azure AI agent names
UUID_SHORT_LENGTH = 8  # Number of characters to use from UUID for unique IDs
MAX_RESPONSE_LENGTH_SENTENCES = 3  # Maximum number of sentences in agent responses
SCENARIO_DATA_DIR = "data/scenarios"  # Default directory for scenario files
DOCKER_APP_PATH = "/app"  # Docker container application path

logger = logging.getLogger(__name__)


class ScenarioManager:
    """Manages training scenarios loaded from YAML files."""

    def __init__(self, scenario_dir: Optional[Path] = None):
        """
        Initialize the scenario manager.

        Args:
            scenario_dir: Directory containing scenario YAML files. If None, uses default location.
        """
        # Determine the correct scenario directory (handles both local and Docker environments)
        self.scenario_dir = determine_scenario_directory(scenario_dir)
        
        # Load all predefined scenarios from YAML files
        self.scenarios = self._load_scenarios()
        
        # Initialize the Microsoft Graph-based scenario generator for personalized scenarios
        self.graph_generator = GraphScenarioGenerator()
        
        # Storage for dynamically generated scenarios (e.g., from Graph API)
        self.generated_scenarios: Dict[str, Any] = {}

    def _load_scenarios(self) -> Dict[str, Any]:
        """
        Load scenarios from YAML files in the scenario directory.

        Returns:
            Dict[str, Any]: Dictionary of scenarios keyed by scenario ID
        """
        scenarios: Dict[str, Any] = {}

        # Check if the scenario directory exists
        if not self.scenario_dir.exists():
            logger.warning("Scenarios directory not found: %s", self.scenario_dir)
            return scenarios

        # Iterate through all files matching the role-play pattern
        for file in self.scenario_dir.glob(f"*{ROLE_PLAY_FILE_SUFFIX}"):
            # Extract the scenario ID from the filename
            scenario_id = self._extract_scenario_id(file)
            
            # Load the scenario data from the YAML file
            scenario = self._load_scenario_file(file)
            
            if scenario:
                # Store the scenario using its ID as the key
                scenarios[scenario_id] = scenario
                logger.info("Loaded scenario: %s", scenario_id)

        logger.info("Total scenarios loaded: %s", len(scenarios))
        return scenarios

    def _extract_scenario_id(self, file: Path) -> str:
        """
        Extract scenario ID from filename by removing the role-play suffix.
        
        Example: "customer-complaint-role-play.prompt.yml" -> "customer-complaint"
        
        Args:
            file: Path object representing the scenario file
            
        Returns:
            str: The extracted scenario ID
        """
        return file.stem.replace(ROLE_PLAY_SUFFIX_REMOVAL, "")

    def _load_scenario_file(self, file: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single scenario file and parse its YAML content.
        
        Args:
            file: Path to the scenario YAML file
            
        Returns:
            Optional[Dict[str, Any]]: Parsed scenario data or None if loading fails
        """
        try:
            with open(file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error("Error loading scenario %s: %s", file, e)
            return None

    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific scenario by ID from either predefined or generated scenarios.

        Args:
            scenario_id: The scenario identifier

        Returns:
            Optional[Dict[str, Any]]: Scenario data or None if not found
        """
        # First check predefined scenarios
        scenario = self.scenarios.get(scenario_id)
        if scenario:
            return scenario

        # Fall back to dynamically generated scenarios
        return self.generated_scenarios.get(scenario_id)

    def list_scenarios(self) -> List[Dict[str, str | bool]]:
        """
        List all available scenarios including predefined and Graph-based options.

        Returns:
            List[Dict[str, str | bool]]: List of scenario summaries with id, name, and description
        """
        # Build list from predefined scenarios
        scenarios: List[Dict[str, str | bool]] = [
            {
                "id": scenario_id,
                "name": scenario_data.get("name", "Unknown"),
                "description": scenario_data.get("description", ""),
            }
            for scenario_id, scenario_data in self.scenarios.items()
        ]

        # Add the special Graph API scenario option for personalized training
        scenarios.append(
            {
                "id": "graph-api",
                "name": "Personalized Scenario",
                "description": "AI-generated scenario based on your upcoming meetings and context from Microsoft Graph",
                "is_graph_scenario": True,
            }
        )

        return scenarios

    def generate_scenario_from_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized scenario based on Microsoft Graph API data.
        
        This creates a training scenario dynamically using the user's calendar,
        emails, and other Microsoft 365 context.

        Args:
            graph_data: The Graph API response data containing user context

        Returns:
            Dict[str, Any]: Generated scenario with unique ID and training content
        """
        # Use the graph generator to create a scenario from the data
        scenario = self.graph_generator.generate_scenario_from_graph(graph_data)

        # Store the generated scenario for later retrieval
        self.generated_scenarios[scenario["id"]] = scenario

        return scenario


class AgentManager:
    """Manages virtual training agents for NBK Banking customer service scenarios."""

    # Base instructions shared by all NBK Banking customer service agents
    # These define the core behavior, tone, and constraints for the AI agent
    BASE_INSTRUCTIONS = f"""

CRITICAL INTERACTION GUIDELINES FOR NBK BANKING CUSTOMER SERVICE:
- You are a helpful and professional NBK (National Bank of Kuwait) customer service representative
- Keep responses SHORT and conversational ({MAX_RESPONSE_LENGTH_SENTENCES} sentences max, as if speaking on phone)
- Provide accurate information about NBK banking services, products, and policies
- Be courteous, patient, and empathetic with customers
- Use natural speech patterns appropriate for customer service
- Always prioritize customer security and privacy
- If you don't know specific account details, guide customers to secure channels
- Speak naturally in either Arabic or English based on customer's language preference
- For Arabic speakers, use clear Modern Standard Arabic that's accessible to Kuwaiti dialect speakers
- Show genuine care and professionalism in every interaction
- Use the Bing Custom Search tool to find accurate, up-to-date information from NBK's official website
- Always cite sources when providing information from NBK website
- If information is not available, politely acknowledge and direct customer to appropriate NBK channels
    """

    def __init__(self):
        """
        Initialize the agent manager.
        
        Sets up Azure credentials, determines whether to use Azure AI Agent Service
        or local instruction-based approach, and initializes the project client if needed.
        """
        # Storage for agent configurations indexed by agent ID
        self.agents: Dict[str, Dict[str, Any]] = {}
        
        # Azure credential for authentication with Azure services
        self.credential = DefaultAzureCredential()
        
        # Flag to determine if using Azure AI Agent Service or local approach
        self.use_azure_ai_agents = config["use_azure_ai_agents"]
        
        # Initialize Azure AI Project client (if applicable)
        self.project_client = self._initialize_project_client()
        
        # Log the initialization mode for debugging
        self._log_initialization_status()

    def _log_initialization_status(self) -> None:
        """
        Log the initialization status to help with debugging and monitoring.
        """
        if self.use_azure_ai_agents:
            logger.info("AgentManager initialized with Azure AI Agent Service support")
        else:
            logger.info("AgentManager initialized with instruction-based approach only")

    def _initialize_project_client(self) -> Optional[AIProjectClient]:
        """
        Initialize the Azure AI Project client for agent management.
        
        Returns None if using pre-configured agents or if project endpoint is not available.
        
        Returns:
            Optional[AIProjectClient]: Initialized client or None
        """
        # For existing Azure AI Foundry agents, we don't need the project client
        # The agent already exists and will be accessed via the Voice Live API
        if self.use_azure_ai_agents:
            agent_id = config.get("agent_id", "")
            if agent_id:
                logger.info("Using pre-configured Azure AI Foundry agent: %s", agent_id)
                return None
        
        # Only initialize project client if using programmatic agent creation
        try:
            project_endpoint = config["project_endpoint"]
            if not project_endpoint:
                logger.warning("PROJECT_ENDPOINT not configured - falling back to instruction-based approach")
                return None

            # Create the Azure AI Project client with credentials
            client = AIProjectClient(
                endpoint=project_endpoint,
                credential=self.credential,
            )
            logger.info("AI Project client initialized with endpoint: %s", project_endpoint)
            return client
        except Exception as e:
            logger.error("Failed to initialize AI Project client: %s", e)
            return None

    def create_agent(self, scenario_id: str, scenario_data: Dict[str, Any]) -> str:
        """
        Create a new virtual agent for a specific training scenario.
        
        This method extracts scenario instructions, combines them with base instructions,
        and creates either an Azure AI agent or a local agent configuration.

        Args:
            scenario_id: The scenario identifier
            scenario_data: The scenario configuration data including instructions and model parameters

        Returns:
            str: The created agent's ID

        Raises:
            Exception: If agent creation fails
        """
        # Extract scenario-specific instructions from the scenario data
        scenario_instructions = scenario_data.get("messages", [{}])[0].get("content", "")
        
        # Combine scenario instructions with base NBK customer service guidelines
        combined_instructions = scenario_instructions + self.BASE_INSTRUCTIONS

        # Extract model configuration from scenario or use defaults
        model_name = scenario_data.get("model", config["model_deployment_name"])
        temperature = scenario_data.get("modelParameters", {}).get("temperature", 0.7)
        max_tokens = scenario_data.get("modelParameters", {}).get("max_tokens", 2000)

        # Create either Azure AI agent or local agent based on configuration
        if self.use_azure_ai_agents and self.project_client:
            return self._create_azure_agent(scenario_id, combined_instructions, model_name, temperature, max_tokens)
        return self._create_local_agent(scenario_id, combined_instructions, model_name, temperature, max_tokens)

    def _create_azure_agent(
        self,
        scenario_id: str,
        instructions: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Use existing Azure AI Agent Service agent configured in Azure AI Foundry.
        
        This method doesn't create a new agent but rather references a pre-configured
        agent in Azure AI Foundry that was set up manually.

        Args:
            scenario_id: The scenario identifier
            instructions: Combined agent instructions
            model: Model deployment name
            temperature: Sampling temperature for generation
            max_tokens: Maximum tokens in response

        Returns:
            str: The agent ID from configuration

        Raises:
            ValueError: If AGENT_ID is not configured
        """
        # Use the existing agent ID from configuration
        agent_id = config.get("agent_id", "")
        
        if not agent_id:
            logger.error("AGENT_ID not configured. Please create an agent in Azure AI Foundry and set AGENT_ID in your .env file")
            raise ValueError("AGENT_ID not configured for Azure AI Agent Service")

        logger.info("Using existing Azure AI agent: %s for scenario: %s", agent_id, scenario_id)

        # Store the agent configuration for reference
        self.agents[agent_id] = self._create_agent_config(
            scenario_id=scenario_id,
            agent_id=agent_id,
            is_azure_agent=True,
            instructions=instructions,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return agent_id

    def _create_local_agent(
        self,
        scenario_id: str,
        instructions: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Create a local agent configuration without Azure AI Agent Service.
        
        This approach stores agent configuration locally and uses direct API calls
        to the model instead of the Azure AI Agent Service.

        Args:
            scenario_id: The scenario identifier
            instructions: Combined agent instructions
            model: Model deployment name
            temperature: Sampling temperature for generation
            max_tokens: Maximum tokens in response

        Returns:
            str: The generated local agent ID

        Raises:
            Exception: If agent configuration creation fails
        """
        try:
            # Generate a unique local agent ID
            agent_id = self._generate_local_agent_id(scenario_id)

            # Create and store the agent configuration
            self.agents[agent_id] = self._create_agent_config(
                scenario_id=scenario_id,
                agent_id=agent_id,
                is_azure_agent=False,
                instructions=instructions,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            logger.info("Created local agent configuration: %s", agent_id)
            return agent_id

        except Exception as e:
            logger.error("Error creating local agent: %s", e)
            raise

    def _generate_agent_name(self, scenario_id: str) -> str:
        """
        Generate a unique agent name for Azure AI agents.
        
        Format: "agent-{scenario_id}-{8_char_uuid}"

        Args:
            scenario_id: The scenario identifier

        Returns:
            str: Unique agent name
        """
        short_uuid = uuid.uuid4().hex[:UUID_SHORT_LENGTH]
        return f"{AZURE_AGENT_NAME_PREFIX}-{scenario_id}-{short_uuid}"

    def _generate_local_agent_id(self, scenario_id: str) -> str:
        """
        Generate a unique local agent ID.
        
        Format: "local-agent-{scenario_id}-{8_char_uuid}"

        Args:
            scenario_id: The scenario identifier

        Returns:
            str: Unique local agent ID
        """
        short_uuid = uuid.uuid4().hex[:UUID_SHORT_LENGTH]
        return f"{AGENT_ID_PREFIX}-{scenario_id}-{short_uuid}"

    def _create_agent_config(
        self,
        scenario_id: str,
        agent_id: str,
        is_azure_agent: bool,
        instructions: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """
        Create standardized agent configuration dictionary.
        
        This structure stores all relevant information about an agent including
        its scenario, instructions, model parameters, and creation metadata.

        Args:
            scenario_id: The scenario identifier
            agent_id: The agent identifier
            is_azure_agent: Whether this is an Azure AI agent or local agent
            instructions: Combined agent instructions
            model: Model deployment name
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Dict[str, Any]: Standardized agent configuration
        """
        result: Dict[str, Any] = {
            "scenario_id": scenario_id,
            "is_azure_agent": is_azure_agent,
            "instructions": instructions,
            "created_at": datetime.now(),
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # For Azure agents, store the Azure-specific agent ID
        if is_azure_agent:
            result["azure_agent_id"] = agent_id

        return result

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent configuration by ID.

        Args:
            agent_id: The agent identifier

        Returns:
            Optional[Dict[str, Any]]: Agent configuration dictionary or None if not found
        """
        return self.agents.get(agent_id)

    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent and clean up resources.
        
        For Azure AI agents, this attempts to delete the agent from Azure AI Agent Service.
        For local agents, this only removes the configuration from memory.

        Args:
            agent_id: The agent identifier to delete
        """
        try:
            if agent_id in self.agents:
                agent_config = self.agents[agent_id]

                # If this is an Azure AI agent, attempt to delete it from the service
                if agent_config.get("is_azure_agent") and self.project_client:
                    try:
                        with self.project_client:
                            self.project_client.agents.delete_agent(agent_id)
                            logger.info("Deleted Azure AI agent: %s", agent_id)
                    except Exception as e:
                        logger.error("Error deleting Azure agent: %s", e)

                # Remove the agent configuration from local storage
                del self.agents[agent_id]
                logger.info("Deleted agent from local storage: %s", agent_id)
        except Exception as e:
            logger.error("Error deleting agent %s: %s", agent_id, e)
