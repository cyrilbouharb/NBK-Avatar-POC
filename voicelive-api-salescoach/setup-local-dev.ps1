# Setup script for local development# Setup script for local development

# This script fetches the necessary API keys and creates a .env file# This script fetches the necessary API keys and creates a .env file



Write-Host "Setting up local development environment..." -ForegroundColor GreenWrite-Host "Setting up local development environment..." -ForegroundColor Green



# Get resource group name# Get resource group name

$resourceGroup = "rg-nbk-avatar"$resourceGroup = "rg-nbk-avatar"



# Get AI Foundry API Key# Get AI Foundry API Key

Write-Host "Fetching AI Foundry API key..." -ForegroundColor YellowWrite-Host "Fetching AI Foundry API key..." -ForegroundColor Yellow

$aiFoundryKey = az cognitiveservices account keys list --resource-group $resourceGroup --name "aifoundry-voicelab-6ng26fguwmnci" --query "key1" -o tsv$aiFoundryKey = az cognitiveservices account keys list `

    --resource-group $resourceGroup `

# Get Speech API Key    --name "aifoundry-voicelab-6ng26fguwmnci" `

Write-Host "Fetching Speech API key..." -ForegroundColor Yellow    --query "key1" -o tsv

$speechKey = az cognitiveservices account keys list --resource-group $resourceGroup --name "speech-voicelab-6ng26fguwmnci" --query "key1" -o tsv

# Get Speech API Key

# Create .env fileWrite-Host "Fetching Speech API key..." -ForegroundColor Yellow

Write-Host "Creating .env file..." -ForegroundColor Yellow$speechKey = az cognitiveservices account keys list `

$envContent = @"    --resource-group $resourceGroup `

# Azure AI Foundry Configuration    --name "speech-voicelab-6ng26fguwmnci" `

AZURE_AI_RESOURCE_NAME=aifoundry-voicelab-6ng26fguwmnci    --query "key1" -o tsv

AZURE_AI_REGION=eastus2

AZURE_AI_PROJECT_NAME=default-project# Create .env file

PROJECT_ENDPOINT=https://aifoundry-voicelab-6ng26fguwmnci.cognitiveservices.azure.com/api/projects/default-projectWrite-Host "Creating .env file..." -ForegroundColor Yellow

$envContent = @"

# Azure OpenAI Configuration# Azure AI Foundry Configuration

AZURE_OPENAI_ENDPOINT=https://aifoundry-voicelab-6ng26fguwmnci.cognitiveservices.azure.com/AZURE_AI_RESOURCE_NAME=aifoundry-voicelab-6ng26fguwmnci

AZURE_OPENAI_API_KEY=$aiFoundryKeyAZURE_AI_REGION=eastus2

MODEL_DEPLOYMENT_NAME=gpt-4oAZURE_AI_PROJECT_NAME=default-project

PROJECT_ENDPOINT=https://aifoundry-voicelab-6ng26fguwmnci.cognitiveservices.azure.com/api/projects/default-project

# Azure Speech Configuration

AZURE_SPEECH_KEY=$speechKey# Azure OpenAI Configuration

AZURE_SPEECH_REGION=eastus2AZURE_OPENAI_ENDPOINT=https://aifoundry-voicelab-6ng26fguwmnci.cognitiveservices.azure.com/

AZURE_SPEECH_LANGUAGE=ar-SAAZURE_OPENAI_API_KEY=$aiFoundryKey

MODEL_DEPLOYMENT_NAME=gpt-4o

# Voice and Avatar Configuration

AZURE_INPUT_TRANSCRIPTION_MODEL=azure-speech# Azure Speech Configuration

AZURE_INPUT_TRANSCRIPTION_LANGUAGE=ar-SAAZURE_SPEECH_KEY=$speechKey

AZURE_INPUT_NOISE_REDUCTION_TYPE=azure_deep_noise_suppressionAZURE_SPEECH_REGION=eastus2

AZURE_VOICE_NAME=ar-SA-ZariyahNeuralAZURE_SPEECH_LANGUAGE=ar-SA

AZURE_VOICE_TYPE=azure-standard

AZURE_AVATAR_CHARACTER=lisa# Voice and Avatar Configuration

AZURE_AVATAR_STYLE=casual-sittingAZURE_INPUT_TRANSCRIPTION_MODEL=azure-speech

AZURE_INPUT_TRANSCRIPTION_LANGUAGE=ar-SA

# Azure SubscriptionAZURE_INPUT_NOISE_REDUCTION_TYPE=azure_deep_noise_suppression

SUBSCRIPTION_ID=5c896c1a-794e-4ddb-8198-b71e0b9171c2AZURE_VOICE_NAME=ar-SA-ZariyahNeural

RESOURCE_GROUP_NAME=rg-nbk-avatarAZURE_VOICE_TYPE=azure-standard

AZURE_AVATAR_CHARACTER=lisa

# Azure AI Agents (set to true to use the agent you created)AZURE_AVATAR_STYLE=casual-sitting

USE_AZURE_AI_AGENTS=true

AGENT_ID=asst_wgsM81Hm1FuLOJemAeEfrYQr# Azure Subscription

SUBSCRIPTION_ID=5c896c1a-794e-4ddb-8198-b71e0b9171c2

# Bing Grounding with Custom SearchRESOURCE_GROUP_NAME=rg-nbk-avatar

BING_GROUNDING_RESOURCE_KEY=fea2aa319c1546ddaa2d09d5dbb9fe65

BING_GROUNDING_RESOURCE_NAME=r-bing-nbk# Azure AI Agents (set to true to use the agent you created)

BING_GROUNDING_CONFIG_ID=USE_AZURE_AI_AGENTS=true

AGENT_ID=asst_wgsM81Hm1FuLOJemAeEfrYQr

# Local Development

PORT=8000# Bing Grounding with Custom Search

HOST=0.0.0.0BING_GROUNDING_RESOURCE_KEY=fea2aa319c1546ddaa2d09d5dbb9fe65

"@BING_GROUNDING_RESOURCE_NAME=r-bing-nbk

BING_GROUNDING_CONFIG_ID=

$envContent | Out-File -FilePath "backend\.env" -Encoding utf8

# Local Development

Write-Host "Success! .env file created at backend\.env" -ForegroundColor GreenPORT=8000

Write-Host ""HOST=0.0.0.0

Write-Host "NOTE: You still need to set BING_GROUNDING_CONFIG_ID in backend\.env" -ForegroundColor Yellow"@

Write-Host "Get it from: https://portal.azure.com -> r-bing-nbk -> Configurations" -ForegroundColor Yellow

Write-Host ""$envContent | Out-File -FilePath "backend\.env" -Encoding utf8

Write-Host "To run locally:" -ForegroundColor Cyan

Write-Host "  1. cd backend" -ForegroundColor WhiteWrite-Host "✓ .env file created at backend\.env" -ForegroundColor Green

Write-Host "  2. pip install -r requirements.txt" -ForegroundColor WhiteWrite-Host ""

Write-Host "  3. python -m src.app" -ForegroundColor WhiteWrite-Host "NOTE: You still need to set BING_GROUNDING_CONFIG_ID in backend\.env" -ForegroundColor Yellow

Write-Host "Get it from: https://portal.azure.com -> r-bing-nbk -> Configurations" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run locally:" -ForegroundColor Cyan
Write-Host "  1. cd backend" -ForegroundColor White
Write-Host "  2. pip install -r requirements.txt" -ForegroundColor White
Write-Host "  3. python -m src.app" -ForegroundColor White
Write-Host ""
Write-Host "Frontend (in another terminal):" -ForegroundColor Cyan
Write-Host "  1. cd frontend" -ForegroundColor White
Write-Host "  2. npm install" -ForegroundColor White
Write-Host "  3. npm run dev" -ForegroundColor White
