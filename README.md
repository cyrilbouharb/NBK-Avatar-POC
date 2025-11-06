# NBK Avatar IP - AI-Powered Banking Customer Service

This repository contains an AI-powered avatar application for National Bank of Kuwait (NBK) customer service, featuring real-time voice conversations in both Arabic and English.

## Project Structure

```
Avatar IP/
├── voicelive-api-salescoach/     # Main application
│   ├── backend/                   # Python Flask backend
│   ├── frontend/                  # React + Vite frontend
│   ├── infra/                     # Azure Bicep infrastructure
│   ├── data/                      # Scenarios and configurations
│   ├── AZURE-DEPLOYMENT-GUIDE.md  # Complete deployment guide
│   ├── TROUBLESHOOTING.md         # Solutions for common issues
│   └── README.md                  # Application documentation
└── azure.yaml                     # Azure Developer CLI configuration
```

## Quick Start

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- Azure subscription with required services:
  - Azure AI Foundry (with GPT-4o deployment)
  - Azure Speech Services
  - Azure Container Apps
  - Bing Grounding (optional)

### Deploy to Azure

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Avatar IP"
   ```

2. **Initialize Azure Developer CLI**
   ```bash
   azd init
   ```

3. **Deploy to Azure**
   ```bash
   azd up
   ```

4. **Configure environment variables** (if Avatar doesn't load)
   
   See [voicelive-api-salescoach/TROUBLESHOOTING.md](voicelive-api-salescoach/TROUBLESHOOTING.md) for detailed instructions on manual Container App configuration.

### Local Development

```bash
cd voicelive-api-salescoach

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start backend (in one terminal)
cd backend
python src/app.py

# Start frontend (in another terminal)
cd frontend
npm run dev
```

## Key Features

- **Bilingual Support** - Seamlessly handles Arabic (ar-SA) and English (en-US) conversations
- **Azure AI Integration** - Powered by GPT-4o and Azure Speech Services
- **Real-time Avatar** - Interactive avatar with natural voice (Andrew Multilingual)
- **Bing Grounding** - Accurate information retrieval from NBK website
- **Azure AI Agent** - Advanced conversational capabilities

## Documentation

- [📘 Azure Deployment Guide](voicelive-api-salescoach/AZURE-DEPLOYMENT-GUIDE.md) - Complete deployment instructions for new Azure subscriptions
- [🔧 Troubleshooting Guide](voicelive-api-salescoach/TROUBLESHOOTING.md) - Solutions for common deployment and runtime issues
- [📖 Application README](voicelive-api-salescoach/README.md) - Application features and architecture

## Configuration

### Avatar Settings

- **Voice**: en-US-AndrewMultilingualNeural
- **Character**: jeff
- **Style**: business
- **Languages**: Arabic (ar-SA), English (en-US)

### Required Azure Resources

- **AI Foundry**: Multi-service cognitive services account with GPT-4o deployment
- **Speech Service**: For voice recognition and synthesis
- **Container Apps**: Hosting environment
- **Container Registry**: Docker image storage
- **Application Insights**: Monitoring and diagnostics
- **Bing Search** (optional): For grounded responses from NBK website

## Architecture

```
┌─────────────────────────────────────┐
│   Azure Container Apps              │
│                                     │
│   ┌─────────────────────────────┐  │
│   │  Frontend (React + Vite)    │  │
│   │  Backend (Python Flask)     │  │
│   └─────────────────────────────┘  │
└─────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Azure  │ │ Speech │ │  Bing  │
│   AI   │ │Service │ │ Search │
│Foundry │ │        │ │        │
└────────┘ └────────┘ └────────┘
```

## Common Issues

### Avatar Not Loading After Deployment

If the Avatar doesn't appear after `azd up` completes:

1. The Container App environment variables may not have been applied
2. See [Troubleshooting Guide - Avatar Not Loading](voicelive-api-salescoach/TROUBLESHOOTING.md#issue-avatar-not-loading-after-successful-deployment)
3. Run the manual Container App update script provided in the troubleshooting guide

### Build Context Too Large

If you see "Uploading build context... 289 MB":

1. Ensure `.dockerignore` includes `**/node_modules/` and `backend/venv/`
2. See [Troubleshooting Guide - Slow Remote Build](voicelive-api-salescoach/TROUBLESHOOTING.md#issue-slow-remote-build-large-context)

### Directory Name Invalid Error

If Docker build fails with "directory name is invalid":

1. Check that `azure.yaml` has correct project path: `voicelive-api-salescoach/backend`
2. See [Troubleshooting Guide](voicelive-api-salescoach/TROUBLESHOOTING.md#issue-docker-build-directory-name-is-invalid)

## Environment Variables

The application requires 27 environment variables to be configured in the Container App. If using existing Azure resources, you'll need to manually configure these after deployment.

Key variables include:
- `AZURE_OPENAI_ENDPOINT`
- `AGENT_ID`
- `AZURE_VOICE_NAME`
- `AZURE_AVATAR_CHARACTER`
- `AZURE_AVATAR_STYLE`
- `AZURE_SPEECH_LANGUAGE`

See [Azure Deployment Guide](voicelive-api-salescoach/AZURE-DEPLOYMENT-GUIDE.md#environment-configuration) for complete list.

## Technologies Used

- **Backend**: Python 3.11, Flask, WebSocket
- **Frontend**: React, TypeScript, Vite
- **Infrastructure**: Azure Bicep, Azure Developer CLI
- **AI Services**: Azure AI Foundry, Speech Services, Bing Search
- **Deployment**: Azure Container Apps, Docker

## Support

For deployment issues and troubleshooting:
1. Check [TROUBLESHOOTING.md](voicelive-api-salescoach/TROUBLESHOOTING.md)
2. Review [AZURE-DEPLOYMENT-GUIDE.md](voicelive-api-salescoach/AZURE-DEPLOYMENT-GUIDE.md)
3. Check application logs: `az containerapp logs show --name voicelab --resource-group <your-rg> --follow`

## License

This is a proof-of-concept project for National Bank of Kuwait.
