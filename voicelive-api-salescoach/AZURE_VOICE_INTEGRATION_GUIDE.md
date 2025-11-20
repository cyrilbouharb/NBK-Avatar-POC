# Azure Voice Live API Integration Guide

## Overview
This document provides comprehensive guidance for integrating with Azure Voice Live API (Real-time Audio) through a backend proxy. It captures all learnings from implementing a voice assistant frontend and can be used by any team to replicate this integration with their own technology stack.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Requirements](#backend-requirements)
3. [Frontend Requirements](#frontend-requirements)
4. [Critical Configuration](#critical-configuration)
5. [WebSocket Protocol](#websocket-protocol)
6. [Audio Processing](#audio-processing)
7. [Common Issues & Solutions](#common-issues--solutions)
8. [Best Practices](#best-practices)

---

## Architecture Overview

### High-Level Flow
```
User (Browser) <--WebSocket--> Backend Proxy <--WebSocket--> Azure Voice Live API
```

### Why a Backend Proxy?
- **Security**: Azure credentials (API keys, Managed Identity) never exposed to frontend
- **Connection Management**: Backend handles Azure authentication and connection lifecycle
- **Session Management**: Pre-configure agent settings on backend for mobile/web clients

### Technology Stack (Reference Implementation)
- **Frontend**: Vanilla JavaScript, Web Audio API, WebSocket (native)
- **Backend**: Python (websockets library, Azure SDK)
- **Azure**: AI Foundry Agent, Voice Live API (API version 2025-10-01)

---

## Backend Requirements

### 1. Azure Configuration

#### Required Azure Resources
- **Azure AI Foundry Project** with:
  - Agent created with desired capabilities
  - Voice capabilities enabled
  - Model deployment (e.g., GPT-4o-mini)
  
#### Authentication
- **Managed Identity** (recommended for production)
- **API Key** (development only)

#### Connection Details
```
Endpoint: https://<region>.voice.speech.azure.com/voice-live/realtime
API Version: 2025-10-01
Agent ID: asst_XXXXXXXXXXXXXXXXXXXX (from AI Foundry)
Project ID: <your-project-id>
Resource ID: <your-resource-id>
```

### 2. Backend WebSocket Proxy Implementation

#### Essential Features
1. **Dual WebSocket Management**
   - Accept client connections from frontend
   - Establish connection to Azure Voice API
   - Bidirectional message forwarding

2. **Authentication with Azure**
```python
# Example header for Azure connection
headers = {
    "api-key": "<your-api-key>",  # OR use Managed Identity token
    "X-Ms-Client-Request-Id": str(uuid.uuid4())
}
```

3. **Session Configuration**
```json
{
    "type": "session.update",
    "session": {
        "modalities": ["text", "audio"],
        "instructions": "<agent instructions>",
        "voice": "shimmer",
        "input_audio_format": "pcm16",
        "output_audio_format": "pcm16",
        "input_audio_transcription": {
            "model": "whisper-1"
        },
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 500,
            "create_response": true
        },
        "tools": [],
        "tool_choice": "auto",
        "temperature": 0.8,
        "max_response_output_tokens": "inf"
    }
}
```

4. **Operating Modes**

**Mobile Backend Mode** (Recommended for Web/Mobile):
- Agent ID configured via environment variable
- Backend sends `session.update` on connection
- Frontend does NOT send `session.update`
- Simpler frontend, better security

**Legacy Mode**:
- Frontend sends `session.update` with agent_id
- Backend forwards configuration
- More flexible but exposes configuration to client

### 3. Message Forwarding

#### Backend → Frontend Messages
Forward these Azure message types to frontend:
- `proxy.connected` (custom message indicating backend ready)
- `session.created`
- `session.updated`
- `input_audio_buffer.speech_started`
- `input_audio_buffer.speech_stopped`
- `input_audio_buffer.committed`
- `conversation.item.input_audio_transcription.completed`
- `response.audio.delta` (**CRITICAL for audio playback**)
- `response.audio_transcript.delta`
- `response.audio_transcript.done`
- `response.done`
- `error`

#### Frontend → Backend Messages
Forward these to Azure:
- `input_audio_buffer.append` (audio chunks from microphone)
- `response.cancel` (optional, for interruptions)

### 4. Connection Management

#### Heartbeat/Keep-Alive
- Implement ping/pong to detect stale connections
- Frontend should send periodic pings when idle
- Backend monitors connection health

#### Reconnection Strategy
- Backend should handle Azure disconnects gracefully
- Frontend implements exponential backoff for reconnection
- Maximum retry attempts recommended: 20

#### Graceful Shutdown
```python
# Close both connections cleanly
await frontend_websocket.close(code=1000, reason="Server shutdown")
await azure_websocket.close(code=1000, reason="Server shutdown")
```

---

## Frontend Requirements

### 1. WebSocket Client

#### Connection Setup
```javascript
const ws = new WebSocket('wss://your-backend.com/ws/voice');

ws.onopen = () => {
    console.log('Connected to backend');
    // DO NOT send session.update if using Mobile Backend Mode
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleMessage(message);
};
```

#### Message Handling
```javascript
function handleMessage(message) {
    switch(message.type) {
        case 'proxy.connected':
            // Backend ready, proceed with UI
            break;
        case 'response.audio.delta':
            // Queue audio for playback
            playAudio(message.delta);
            break;
        case 'conversation.item.input_audio_transcription.completed':
            // Display user transcript
            showUserMessage(message.transcript);
            break;
        case 'response.audio_transcript.done':
            // Display assistant transcript
            showAssistantMessage(message.transcript);
            break;
        case 'error':
            // Handle errors
            console.error('Error:', message.error);
            break;
    }
}
```

### 2. Audio Input (Microphone)

#### Required Format
- **Encoding**: PCM16 (16-bit signed integer)
- **Sample Rate**: 24kHz
- **Channels**: Mono (1 channel)
- **Transmission**: Base64-encoded chunks

#### Implementation Steps

**Step 1: Request Microphone Access**
```javascript
const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
        channelCount: 1,
        sampleRate: 24000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
    }
});
```

**Step 2: Create Audio Context**
```javascript
const audioContext = new AudioContext({ sampleRate: 24000 });
const source = audioContext.createMediaStreamSource(stream);
```

**Step 3: Process Audio (Convert to PCM16)**
```javascript
// Use ScriptProcessorNode (deprecated but widely supported)
// OR AudioWorkletNode (modern, better performance)

const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
    const float32Data = e.inputBuffer.getChannelData(0);
    const pcm16Data = convertFloat32ToPCM16(float32Data);
    const base64Audio = arrayBufferToBase64(pcm16Data);
    
    // Send to backend
    ws.send(JSON.stringify({
        type: 'input_audio_buffer.append',
        audio: base64Audio
    }));
};

source.connect(processor);
processor.connect(audioContext.destination);
```

**Step 4: Float32 to PCM16 Conversion**
```javascript
function convertFloat32ToPCM16(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    
    for (let i = 0; i < float32Array.length; i++) {
        let sample = Math.max(-1, Math.min(1, float32Array[i]));
        sample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        view.setInt16(i * 2, sample, true); // true = little-endian
    }
    
    return buffer;
}
```

**Step 5: Base64 Encoding**
```javascript
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}
```

### 3. Audio Output (Playback)

#### Required Format (from Azure)
- **Encoding**: PCM16 (base64-encoded)
- **Sample Rate**: 24kHz
- **Channels**: Mono

#### Critical Implementation Detail: SEQUENTIAL PLAYBACK

**❌ WRONG APPROACH (Common Mistake):**
```javascript
// This plays all chunks simultaneously, causing garbled audio
ws.on('audio-delta', (data) => {
    const audioBuffer = convertToAudioBuffer(data.delta);
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start(); // ALL chunks play at same time!
});
```

**✅ CORRECT APPROACH (Queued Playback):**
```javascript
// Audio queue for sequential playback
let playbackQueue = [];
let isPlaying = false;

ws.on('audio-delta', (data) => {
    const audioBuffer = convertToAudioBuffer(data.delta);
    playbackQueue.push(audioBuffer);
    
    if (!isPlaying) {
        playNextInQueue();
    }
});

function playNextInQueue() {
    if (playbackQueue.length === 0) {
        isPlaying = false;
        return;
    }
    
    isPlaying = true;
    const audioBuffer = playbackQueue.shift();
    
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    
    source.onended = () => {
        playNextInQueue(); // Play next chunk when current ends
    };
    
    source.start();
}
```

#### Audio Conversion Steps

**Step 1: Base64 to ArrayBuffer**
```javascript
function base64ToArrayBuffer(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}
```

**Step 2: PCM16 to Float32**
```javascript
function pcm16ToFloat32(arrayBuffer) {
    const view = new DataView(arrayBuffer);
    const float32 = new Float32Array(arrayBuffer.byteLength / 2);
    
    for (let i = 0; i < float32.length; i++) {
        const int16 = view.getInt16(i * 2, true); // little-endian
        float32[i] = int16 / (int16 < 0 ? 0x8000 : 0x7FFF);
    }
    
    return float32;
}
```

**Step 3: Create Audio Buffer**
```javascript
function convertToAudioBuffer(base64Audio) {
    const arrayBuffer = base64ToArrayBuffer(base64Audio);
    const float32Data = pcm16ToFloat32(arrayBuffer);
    
    const audioBuffer = audioContext.createBuffer(
        1, // mono
        float32Data.length,
        24000 // 24kHz
    );
    
    audioBuffer.getChannelData(0).set(float32Data);
    return audioBuffer;
}
```

### 4. Voice Activity Detection (VAD)

#### Server-Side VAD (Recommended)
Azure handles speech detection automatically with `turn_detection.type = "server_vad"`.

**Frontend Behavior:**
- Start recording when user clicks/presses button
- Keep streaming audio continuously
- Do NOT send `input_audio_buffer.commit` manually
- Azure detects silence and triggers response automatically

**After User Stops Speaking:**
```javascript
function stopRecording() {
    // Keep streaming for 1-2 seconds after button release
    // This gives VAD time to detect the trailing silence
    setTimeout(() => {
        actuallyStopRecording();
    }, 1500);
}
```

#### Client-Side VAD (Optional)
If you want manual control, set `turn_detection: null` in backend config and send:
```javascript
ws.send(JSON.stringify({
    type: 'input_audio_buffer.commit'
}));
```

**⚠️ WARNING:** Cannot use both server VAD and manual commit. Choose one.

---

## Critical Configuration

### 1. Auto-Commit Setting
```javascript
// Frontend config
const config = {
    autoCommit: false  // MUST be false when using server_vad
};
```

**Why this matters:**
- `autoCommit: true` sends `input_audio_buffer.commit` after each audio chunk
- Server-side VAD does NOT accept manual commits
- Results in error: "input_audio_buffer.commit is not supported when server side VAD is enabled"

### 2. Session Configuration (Backend)

**Critical Settings:**
```json
{
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.5,           // Sensitivity (0.0-1.0)
        "prefix_padding_ms": 300,   // Include audio before speech
        "silence_duration_ms": 500, // How long to wait for silence
        "create_response": true     // Auto-generate response
    }
}
```

**Tuning Guidelines:**
- `threshold`: Lower = more sensitive (picks up quieter speech)
- `silence_duration_ms`: Higher = waits longer before responding (better for pauses)
- Recommended starting values: threshold=0.5, silence=500ms

### 3. Audio Format Consistency

**Every component must use:**
- 24kHz sample rate
- Mono (1 channel)
- PCM16 encoding
- Little-endian byte order

### 4. WebSocket URL Format
```
wss://your-backend.com/ws/voice
```

**Must be:**
- Secure WebSocket (`wss://` not `ws://`)
- CORS-enabled on backend
- Accessible from frontend domain

---

## WebSocket Protocol

### Message Types Reference

#### Frontend → Backend

**Send Audio Chunk:**
```json
{
    "type": "input_audio_buffer.append",
    "audio": "<base64-encoded-pcm16>"
}
```

**Cancel Response (Optional):**
```json
{
    "type": "response.cancel"
}
```

**Heartbeat Ping:**
```json
{
    "type": "ping"
}
```

#### Backend → Frontend

**Proxy Ready:**
```json
{
    "type": "proxy.connected",
    "message": "Connected to Azure Voice API"
}
```

**Session Created:**
```json
{
    "type": "session.created",
    "session": { /* session details */ }
}
```

**Speech Started:**
```json
{
    "type": "input_audio_buffer.speech_started"
}
```

**Speech Stopped:**
```json
{
    "type": "input_audio_buffer.speech_stopped"
}
```

**User Transcript:**
```json
{
    "type": "conversation.item.input_audio_transcription.completed",
    "transcript": "Hey, how are you?",
    "item_id": "item_xxx"
}
```

**Audio Response Chunk:**
```json
{
    "type": "response.audio.delta",
    "delta": "<base64-encoded-pcm16>",
    "response_id": "resp_xxx",
    "item_id": "item_xxx",
    "output_index": 0,
    "content_index": 0
}
```

**Assistant Transcript Chunk:**
```json
{
    "type": "response.audio_transcript.delta",
    "delta": "Hello! I'm doing ",
    "response_id": "resp_xxx"
}
```

**Assistant Transcript Complete:**
```json
{
    "type": "response.audio_transcript.done",
    "transcript": "Hello! I'm doing well, thank you for asking.",
    "response_id": "resp_xxx"
}
```

**Response Complete:**
```json
{
    "type": "response.done",
    "response": { /* response details */ }
}
```

**Error:**
```json
{
    "type": "error",
    "error": {
        "type": "invalid_request_error",
        "code": "invalid_value",
        "message": "Error description"
    }
}
```

### Close Codes

| Code | Meaning | Action |
|------|---------|--------|
| 1000 | Normal closure | No action needed |
| 1001 | Going away | Reconnect |
| 1002 | Protocol error | Check message format |
| 1003 | Unsupported data | Check audio encoding |
| 1006 | Abnormal closure | Reconnect with backoff |
| 1011 | Server error | Retry after delay |
| 4000-4999 | Custom errors | Check error message |

---

## Audio Processing

### Browser Audio Pipeline

```
Microphone → MediaStream → AudioContext → ScriptProcessor/Worklet
    ↓                                           ↓
Float32 PCM (browser native)              Convert to PCM16
    ↓                                           ↓
    └─────────────────→ Base64 Encode ─────────┘
                              ↓
                        WebSocket Send
```

### Playback Pipeline

```
WebSocket Receive → Base64 Decode → PCM16 ArrayBuffer
                         ↓
                   Convert to Float32
                         ↓
                   Create AudioBuffer
                         ↓
                   Queue for Playback
                         ↓
                   BufferSourceNode → Speakers
```

### Performance Considerations

1. **Chunk Size**
   - Recording: 4096 samples (~170ms at 24kHz)
   - Playback: Variable (from Azure, typically 500-800ms chunks)

2. **Latency Sources**
   - Network RTT: 20-100ms
   - Audio buffering: 170ms (recording)
   - VAD processing: 300-500ms (server-side)
   - Total: ~500-800ms typical

3. **Memory Management**
   - Clear playback queue on new recording
   - Dispose audio buffers after playback
   - Monitor for memory leaks in long sessions

---

## Common Issues & Solutions

### Issue 1: "Cannot commit while server_vad is enabled"
**Cause:** Frontend sending `input_audio_buffer.commit` with server-side VAD enabled.

**Solution:**
- Set `autoCommit: false` in frontend
- Remove any manual commit sending
- Let server VAD handle turn detection

### Issue 2: Garbled/Fast/Overlapping Audio
**Cause:** Playing audio chunks simultaneously instead of sequentially.

**Solution:**
- Implement playback queue (see Audio Output section)
- Only start next chunk after previous ends
- Use `source.onended` callback for chaining

### Issue 3: No Audio Response
**Causes:**
- Recording stopped too quickly (VAD didn't detect silence)
- Audio format mismatch
- Missing `response.audio.delta` handler

**Solutions:**
- Keep streaming 1-2 seconds after user stops speaking
- Verify PCM16, 24kHz, mono format
- Check WebSocket message handlers

### Issue 4: Connection Drops Frequently
**Causes:**
- No heartbeat/ping mechanism
- Idle timeout on proxy/cloud
- Network instability

**Solutions:**
- Implement ping every 15-30 seconds when idle
- Add exponential backoff reconnection
- Monitor connection health

### Issue 5: VAD Too Sensitive/Not Sensitive Enough
**Cause:** Incorrect `turn_detection.threshold` setting.

**Solution:**
- Lower threshold (0.3-0.4) for quiet environments
- Higher threshold (0.6-0.7) for noisy environments
- Increase `silence_duration_ms` for users with pauses

### Issue 6: Audio Cutting Off Mid-Sentence
**Cause:** Queue cleared prematurely or response interruption.

**Solution:**
- Don't clear queue on `response.done`
- Only clear queue when user starts new recording
- Let audio finish naturally before interruption

---

## Best Practices

### Security
1. **Never expose Azure credentials to frontend**
   - Use backend proxy for all Azure communication
   - Implement authentication for backend WebSocket
   - Validate all frontend inputs on backend

2. **Use HTTPS/WSS exclusively**
   - Mixed content warnings break functionality
   - Required for microphone access in modern browsers

3. **Implement rate limiting**
   - Prevent abuse of voice API
   - Monitor usage costs

### User Experience
1. **Visual Feedback**
   - Show connection status
   - Indicate when recording
   - Display processing state
   - Show volume/activity indicator

2. **Error Handling**
   - Graceful degradation on errors
   - Clear error messages to users
   - Automatic reconnection attempts

3. **Interruption Support**
   - Allow user to interrupt assistant response
   - Clear audio queue when starting new recording
   - Cancel pending responses

### Performance
1. **Lazy Audio Context Creation**
   - Create AudioContext only after user interaction
   - Avoids browser autoplay restrictions

2. **Efficient Encoding/Decoding**
   - Reuse ArrayBuffers where possible
   - Minimize base64 conversions
   - Use TypedArrays for performance

3. **Connection Pooling**
   - Reuse WebSocket connections
   - Implement connection warmup for frequently used sessions

### Testing
1. **Test Different Network Conditions**
   - Throttle bandwidth (mobile simulation)
   - Test reconnection on dropouts
   - Verify audio quality under packet loss

2. **Browser Compatibility**
   - Test on Chrome, Safari, Firefox, Edge
   - Mobile browsers (iOS Safari, Chrome Android)
   - Handle vendor prefixes if needed

3. **Audio Device Testing**
   - Different microphones
   - Bluetooth headsets
   - Built-in vs. external speakers

---

## Example Implementations

### Minimal Frontend (Vanilla JS)
```javascript
// 1. Setup
const ws = new WebSocket('wss://backend.com/ws/voice');
const audioContext = new AudioContext({ sampleRate: 24000 });
let playbackQueue = [];
let isPlaying = false;

// 2. WebSocket handlers
ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    
    if (msg.type === 'response.audio.delta') {
        const buffer = base64ToPCM16(msg.delta);
        const audioBuffer = createAudioBuffer(buffer);
        playbackQueue.push(audioBuffer);
        if (!isPlaying) playNext();
    }
};

// 3. Recording
async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: 24000, channelCount: 1 }
    });
    
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    
    processor.onaudioprocess = (e) => {
        const float32 = e.inputBuffer.getChannelData(0);
        const pcm16 = float32ToPCM16(float32);
        const base64 = arrayBufferToBase64(pcm16);
        
        ws.send(JSON.stringify({
            type: 'input_audio_buffer.append',
            audio: base64
        }));
    };
    
    source.connect(processor);
    processor.connect(audioContext.destination);
}

// 4. Playback
function playNext() {
    if (playbackQueue.length === 0) {
        isPlaying = false;
        return;
    }
    
    isPlaying = true;
    const buffer = playbackQueue.shift();
    const source = audioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContext.destination);
    source.onended = playNext;
    source.start();
}
```

### Backend Proxy (Python)
```python
import asyncio
import websockets
import json

async def handle_client(client_ws):
    # Connect to Azure
    azure_ws = await websockets.connect(
        "wss://region.voice.speech.azure.com/voice-live/realtime?api-version=2025-10-01",
        extra_headers={"api-key": "YOUR_API_KEY"}
    )
    
    # Send session config
    await azure_ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "silence_duration_ms": 500
            }
        }
    }))
    
    # Bidirectional forwarding
    async def forward_to_azure():
        async for msg in client_ws:
            await azure_ws.send(msg)
    
    async def forward_to_client():
        async for msg in azure_ws:
            await client_ws.send(msg)
    
    await asyncio.gather(forward_to_azure(), forward_to_client())

# Start server
start_server = websockets.serve(handle_client, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

---

## Technology-Agnostic Checklist

Use this checklist regardless of your stack:

### Backend ✓
- [ ] WebSocket server accepts client connections
- [ ] Establishes WebSocket to Azure Voice Live API
- [ ] Handles Azure authentication (API key or Managed Identity)
- [ ] Sends `session.update` with agent configuration
- [ ] Forwards client audio to Azure
- [ ] Forwards Azure responses to client
- [ ] Implements heartbeat/connection monitoring
- [ ] Handles graceful shutdown and reconnection

### Frontend ✓
- [ ] WebSocket client connects to backend
- [ ] Requests microphone permission
- [ ] Captures audio at 24kHz mono
- [ ] Converts Float32 to PCM16
- [ ] Base64 encodes audio
- [ ] Sends audio chunks via WebSocket
- [ ] Receives and parses WebSocket messages
- [ ] Decodes base64 audio from `response.audio.delta`
- [ ] Converts PCM16 to Float32 for playback
- [ ] **Implements sequential audio queue** (critical!)
- [ ] Displays transcripts
- [ ] Handles errors and disconnections
- [ ] Implements reconnection with backoff

### Configuration ✓
- [ ] `autoCommit: false` when using server VAD
- [ ] Consistent 24kHz sample rate throughout
- [ ] PCM16 encoding for all audio
- [ ] Mono (1 channel) audio
- [ ] Little-endian byte order
- [ ] Secure WebSocket (wss://) connections

### Testing ✓
- [ ] Audio plays sequentially, not overlapping
- [ ] User can interrupt assistant
- [ ] VAD detects speech correctly
- [ ] No cutoffs mid-sentence
- [ ] Reconnection works after disconnect
- [ ] Works on target browsers/devices
- [ ] Acceptable latency (<1 second typical)

---

## Additional Resources

### Azure Documentation
- [Azure Voice Live API Reference](https://learn.microsoft.com/azure/ai-services/speech-service/real-time-voice-api)
- [AI Foundry Agents](https://learn.microsoft.com/azure/ai-foundry/agents)
- [Managed Identity Authentication](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/)

### Web Standards
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [MediaStream API](https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_API)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

### Performance
- [AudioWorklet (modern alternative to ScriptProcessor)](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet)
- [WebSocket Performance Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications)

---

## Troubleshooting Decision Tree

```
Audio not playing?
├─ Check browser console for errors
├─ Verify response.audio.delta messages received
├─ Confirm base64 decoding works
├─ Test with single audio chunk
└─ Verify sequential playback queue

VAD not detecting speech?
├─ Ensure recording started
├─ Check microphone permissions
├─ Verify audio chunks being sent
├─ Keep streaming after speech stops
└─ Adjust threshold/silence_duration_ms

Connection issues?
├─ Check WebSocket URL
├─ Verify CORS on backend
├─ Test backend independently
├─ Check Azure credentials
└─ Monitor connection health

Audio garbled/fast?
├─ Verify sequential playback (not parallel)
├─ Check sample rate consistency (24kHz)
├─ Confirm PCM16 encoding
└─ Test with queue implementation
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-20 | Initial documentation based on implementation learnings |

---

## Support

For issues specific to:
- **Azure Services**: Contact Azure Support or AI Foundry team
- **This Implementation**: Reference INTEGRATION.md and README.md in this repository
- **General Web Audio**: MDN Web Docs and Stack Overflow

---

**End of Integration Guide**
