# ---------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See LICENSE in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Flask application for the upskilling agent."""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, cast

import simple_websocket.ws  # pyright: ignore[reportMissingTypeStubs]
from flask import Flask, jsonify, request
from flask_sock import Sock  # pyright: ignore[reportMissingTypeStubs]

from src.config import config
from src.services.analyzers import ConversationAnalyzer, PronunciationAssessor
from src.services.managers import AgentManager, ScenarioManager
from src.services.websocket_handler import VoiceProxyHandler

# Constants
WEBSOCKET_ENDPOINT = "/ws/voice"

# API endpoints - MOBILE BACKEND MODE: Minimal endpoints for health check and config
API_CONFIG_ENDPOINT = "/api/config"
API_HEALTH_ENDPOINT = "/api/health"

# HTTP status codes
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application - MOBILE BACKEND MODE: No static file serving
app = Flask(__name__)
sock = Sock(app)

# Initialize managers and analyzers
scenario_manager = ScenarioManager()
agent_manager = AgentManager()
conversation_analyzer = ConversationAnalyzer()
pronunciation_assessor = PronunciationAssessor()
voice_proxy_handler = VoiceProxyHandler(agent_manager)


@app.route(API_HEALTH_ENDPOINT)
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "NBK Banking Voice Backend",
        "websocket_endpoint": WEBSOCKET_ENDPOINT
    })


@app.route(API_CONFIG_ENDPOINT)
def get_config():
    """Get client configuration - returns WebSocket endpoint."""
    return jsonify({
        "proxy_enabled": True,
        "ws_endpoint": WEBSOCKET_ENDPOINT,
        "mode": "mobile_backend",
        "scenario": "nbk-banking"
    })


@sock.route(WEBSOCKET_ENDPOINT)  # pyright: ignore[reportUnknownMemberType]
def voice_proxy(ws: simple_websocket.ws.Server):
    """WebSocket endpoint for voice proxy."""

    logger.info("New WebSocket connection")

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(voice_proxy_handler.handle_connection(ws))


def main():
    """Run the Flask application."""
    host = config["host"]
    port = config["port"]
    print(f"Starting NBK Banking Voice Backend on http://{host}:{port}")
    print(f"WebSocket endpoint: ws://{host}:{port}{WEBSOCKET_ENDPOINT}")
    print(f"Health check: http://{host}:{port}{API_HEALTH_ENDPOINT}")

    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(host=host, port=port, debug=debug_mode)


if __name__ == "__main__":
    main()
