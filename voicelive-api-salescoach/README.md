# NBK Banking Customer Service Avatar

A bilingual (Arabic/English) AI-powered banking customer service avatar for National Bank of Kuwait, built on Azure.

---

## Overview

NBK Banking Customer Service Avatar is an AI-powered virtual assistant for National Bank of Kuwait customers. Using Azure AI services and Bing Custom Search grounding, it provides accurate information about NBK's banking services and products through natural voice conversations in both Arabic and English.

### Features

- **Bilingual Voice Conversations** - Interact naturally in Arabic or English using Azure Voice Live API
- **Grounded on NBK Website** - Uses Bing Custom Search to provide accurate, up-to-date information from NBK's official website
- **Real-time Voice Assistant** - Natural conversation flow with Azure Speech Services
- **Professional Banking Support** - Assists with inquiries about accounts, cards, loans, investments, and digital banking
- **Secure by Design** - Never asks for sensitive credentials, guides customers to secure channels for account-specific needs

---

## Architecture

<table>
<tr>
<td width="500">
<img src="docs/assets/architecture.png" alt="Architecture Diagram" width="500"/>
</td>
<td>

The application leverages multiple Azure AI services to deliver real-time voice-based banking customer service:

- **Azure AI Foundry** - AI platform including:
  - **Voice Live API** for real-time speech-to-speech conversations and avatar simulation
  - **Large language models (GPT-4o)** as underlying LLM for customer service responses
  - **Speech Services** for post-conversation pronunciation and fluency assessment
  - **Optional AI Agent Service** for advanced conversation management
- **React + Fluent UI** - Modern web interface for seamless customer interaction
- **Python Flask** - Backend API and WebSocket communication

**Conversation Flow:**

User speech → Voice Live API → GPT-4o processing → AI agent response → Performance analysis → Detailed feedback

</td>
</tr>
</table>

---

## Getting Started

### Deploy to Azure

```bash
cd voicelive-api-salescoach
azd auth login
azd up
```

**📖 See [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) for complete deployment instructions.**

### Local Development

1. **Use Dev Container** (Recommended)
   - Open in VS Code and select "Reopen in Container" when prompted
   - All dependencies and tools are pre-configured

2. **Fill in the .env file**
   - Copy `.env.template` to `.env`
   - Fill in your Azure AI Foundry and Speech service keys and endpoints

3. **Build and run**
   ```bash
   # Build the application
   ./scripts/build.sh

   # Start the server
   cd backend && python src/app.py
   ```

Visit `http://localhost:8000` to start using the avatar!

---

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
</p>
