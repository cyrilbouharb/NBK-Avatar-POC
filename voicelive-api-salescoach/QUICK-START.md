# NBK Banking Avatar - Quick Start Guide

## Step 1: Deploy Infrastructure

```bash
azd up
```

Wait for deployment to complete (~8-10 minutes). Note the application URL from the output.

---

## Step 2: Configure Bing Custom Search

### 2.1 Access Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group (e.g., `rg-nbk-avatar`)
3. Find the Bing Grounding resource (starts with `bing-grounding-`)

### 2.2 Create Configuration
1. Click **Resource Management** → **Configurations**
2. Click **Create a new configuration**
3. Fill in the following:

**Configuration Name**: `NBK-Website-Search`

**Allowed Domains** (copy and paste these):
```
https://www.nbk.com/kuwait
https://www.nbk.com/kuwait/personal/cards/credit-cards.html
https://www.nbk.com/kuwait/investments/nbk-invest-app/guided-investments.html
```

**Options**:
- ✅ Include subpages
- Market: `ar-SA` (Arabic) and `en-US` (English)

4. Click **Save**
5. **COPY THE CONFIGURATION ID** (you'll see it in the configuration list)

---

## Step 3: Update Environment

```bash
# Set the configuration ID (replace with your actual ID)
azd env set BING_GROUNDING_CONFIG_ID <your-configuration-id>

# Redeploy to apply changes
azd up
```

---

## Step 4: Test the Avatar

1. Open the application URL (from Step 1 output)
2. Click the microphone button

**Test in Arabic:**
```
مرحبا، أريد معلومات عن بطاقات الائتمان في البنك الوطني
```
(Hello, I want information about credit cards at National Bank)

**Test in English:**
```
Hello, can you tell me about NBK credit cards?
```

**Expected**: The avatar should respond with information and **cite NBK website sources**.

---

## Troubleshooting

### No Bing Citations in Responses
- **Cause**: Configuration ID not set or incorrect
- **Fix**: 
  ```bash
  azd env get-values | grep BING
  azd env set BING_GROUNDING_CONFIG_ID <correct-id>
  azd up
  ```

### Arabic Voice Not Working
- **Cause**: Voice not available in region
- **Fix**: Check Speech Services region or try alternative voice:
  ```bash
  azd env set VOICE_NAME ar-SA-HamedNeural
  azd up
  ```

### Agent Not Found
- **Cause**: First-time initialization needed
- **Fix**: Wait 30 seconds, refresh page, try again

---

## Quick Reference

### View Environment Variables
```bash
azd env get-values
```

### View Logs
```bash
azd logs
```

### Redeploy After Changes
```bash
azd up
```

### Delete Everything
```bash
azd down --purge
```

---

## NBK Domains to Add Later (Optional)

As you expand the avatar's knowledge, add these domains in the Bing configuration:

**Personal Banking:**
- `https://www.nbk.com/kuwait/personal/accounts.html`
- `https://www.nbk.com/kuwait/personal/loans.html`

**Digital Banking:**
- `https://www.nbk.com/kuwait/personal/digital-banking.html`
- `https://www.nbk.com/kuwait/personal/nbk-mobile-banking.html`

**Business Banking:**
- `https://www.nbk.com/kuwait/business.html`

**Investment:**
- `https://www.nbk.com/kuwait/investments.html`

**About NBK:**
- `https://www.nbk.com/kuwait/about-nbk.html`
- `https://www.nbk.com/kuwait/contact-us.html`

---

## Support

- **Deployment Guide**: See `DEPLOYMENT-GUIDE.md` for detailed instructions
- **Full Changes**: See `NBK-TRANSFORMATION-SUMMARY.md` for complete documentation
- **Azure Portal**: [portal.azure.com](https://portal.azure.com)
- **AI Foundry Portal**: [ai.azure.com](https://ai.azure.com)
