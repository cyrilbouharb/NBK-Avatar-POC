# Local Development Setup

## Quick Start

### 1. Backend Setup

```powershell
cd backend
pip install -r requirements.txt
python -m src.app
```

The backend will start on `http://localhost:8000`

### 2. Frontend Setup (in a new terminal)

```powershell
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

## Testing the API

Test if the backend is working:

```powershell
# Test health endpoint
curl http://localhost:8000/

# Test scenarios endpoint
curl http://localhost:8000/api/scenarios

# Test config endpoint
curl http://localhost:8000/api/config
```

## Environment Variables

All environment variables are configured in `backend\.env`. The file has been created with values from your deployed Azure resources.

**Important**: You need to add your `BING_GROUNDING_CONFIG_ID` in the `.env` file:
1. Go to Azure Portal: https://portal.azure.com
2. Navigate to resource `r-bing-nbk`
3. Click on "Configurations"
4. Create a configuration named "NBK-Website-Search"
5. Add these domains:
   - https://www.nbk.com/kuwait
   - https://www.nbk.com/kuwait/personal/cards/credit-cards.html
   - https://www.nbk.com/investments/nbk-invest-app/guided-investments.html
6. Copy the Configuration ID
7. Update `backend\.env`: `BING_GROUNDING_CONFIG_ID=<your-config-id>`

## Troubleshooting

### Backend won't start
- Make sure you're in the `backend` directory
- Check that Python 3.11+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check `.env` file exists in `backend` directory

### Frontend won't start
- Make sure you're in the `frontend` directory
- Check that Node.js is installed: `node --version`
- Install dependencies: `npm install`

### "Start Training" button not working
- Check browser console for errors (F12)
- Verify backend is running on port 8000
- Check that the scenario exists: `curl http://localhost:8000/api/scenarios`
- Look at backend console for any error messages

### WebSocket connection fails
- Make sure both backend (port 8000) and frontend (port 5173) are running
- Check browser console for WebSocket errors
- Verify firewall isn't blocking local connections

## What Changed from Original

The application has been transformed from a sales training coach to an NBK banking customer service avatar:

1. **Language**: Changed from English to Arabic (ar-SA-ZariyahNeural) with English support
2. **Agent Instructions**: Updated to banking customer service context
3. **Bing Grounding**: Added Bing Custom Search to ground responses on NBK website
4. **Scenario**: Created `nbk-banking-role-play.prompt.yml` for banking interactions

## Files Modified

- `backend/src/config.py` - Updated defaults to Arabic, added Bing config
- `backend/src/services/managers.py` - Updated agent instructions, added Bing tool
- `data/scenarios/nbk-banking-role-play.prompt.yml` - New banking scenario
- `infra/resources.bicep` - Removed Bing resource (created manually)

No breaking changes were made to the core application logic.
