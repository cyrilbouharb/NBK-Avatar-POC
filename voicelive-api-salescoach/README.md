# NBK Banking Customer Service Avatar

A bilingual (Arabic/English) AI-powered banking customer service avatar for National Bank of Kuwait, built on Azure.

---

## Overview

NBK Banking Customer Service Avatar is an AI-powered virtual assistant for National Bank of Kuwait customers. Using Azure AI services and Bing Custom Search grounding, it provides accurate information about NBK's banking services and products through natural voice conversations in both Arabic and English.

### Features

- **Bilingual Voice Conversations** - Interact naturally in Arabic (Kuwaiti-friendly dialect) or English using Azure Voice Live API
- **Grounded on NBK Website** - Uses Bing Custom Search to provide accurate, up-to-date information from NBK's official website
- **Real-time Voice Assistant** - Natural conversation flow with Azure Speech Services
- **Professional Banking Support** - Assists with inquiries about accounts, cards, loans, investments, and digital banking
- **Secure by Design** - Never asks for sensitive credentials, guides customers to secure channels for account-specific needs

## Getting Started

### Deploy to Azure

**📚 For complete deployment instructions and troubleshooting, see:**
- [AZURE-DEPLOYMENT-GUIDE.md](AZURE-DEPLOYMENT-GUIDE.md) - Comprehensive deployment guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solutions for common issues

**Quick Start:**

1. **Deploy to Azure**:
   ```bash
   azd up
   ```

2. **Configure Container App Environment** (if Avatar doesn't load):
   
   If the Avatar doesn't appear after deployment, you may need to manually configure the Container App environment variables. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#issue-avatar-not-loading-after-successful-deployment) for detailed instructions.

3. **Configure Bing Custom Search**:
   - After deployment, go to the Bing Grounding with Custom Search resource in Azure Portal
   - Create a new configuration instance
   - Add NBK website domains (e.g., `https://www.nbk.com`, `https://www.nbk.com.kw`)
   - Note the Configuration ID
   
4. **Update Environment Variable**:
   ```bash
   azd env set BING_GROUNDING_CONFIG_ID <your-config-id>
   azd up
   ```

5. **Access your application**:
   The deployment will output the URL where your application is running.

### Local Development

This project includes a dev container for easy setup and a build script for  development.

1. **Use Dev Container** (Recommended)
   - Open in VS Code and select "Reopen in Container" when prompted
   - All dependencies and tools are pre-configured

2. **Fill in the .env file**
   - Copy `.env.template` to `.env`
   - Fill in your Azure AI Foundry and Speech service keys and endpoints (you can run `azd provision` to create these resources if you haven't already)

3. **Build and run**
   ```bash
   # Build the application
   ./scripts/build.sh

   # Start the server
   cd backend && python src/app.py
   ```

Visit `http://localhost:8000` to start the application.

## Architecture

The application leverages multiple Azure AI services to deliver real-time voice-based customer service:

- **Azure AI Foundry** - AI platform including:
  - Voice Live API for real-time speech-to-speech conversations and avatar simulation
  - Large language models (GPT-4o) as underlying LLM for conversation
  - Speech Services for voice recognition and synthesis
  - Optional AI Agent Service for advanced conversational AI
- **React + Vite** - Modern web interface
- **Python Flask** - Backend API and WebSocket communication

**Conversation Flow:** User speech → Voice Live API → GPT-4o processing → AI agent response → Avatar synthesis → User feedback
Any use of third-party trademarks or logos are subject to those third-party's policies.
Any use of third-party trademarks or logos are subject to those third-party's policies.



<p align="center">
   <br/>
   <br/>
   Made with ❤️ in 🇨🇭
</p>
