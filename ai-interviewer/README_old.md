# AI Interviewer

Enterprise-grade AI interviewer with FastAPI backend, WebSocket dialogue, Google Gemini AI, Three.js realistic avatar, Web Speech API voice (both TTS and STT), and professional interview flow.

## Features

✨ **Realistic Avatar**
- Human-like 3D face with skin tone and proportional body
- Blinking eyes with auto-blink animation (3-7 second intervals)
- Smooth mouth animation synchronized with speech
- Facial expressions based on interview state (smiling, thinking, listening, etc.)
- Natural head and body movement during idle

🎙️ **Voice Capabilities**
- **Text-to-Speech (TTS)**: Avatar speaks AI responses via Web Speech API
- **Speech-to-Text (STT)**: Click 🎤 button to speak your answers instead of typing
- Natural speech synthesis with proper pacing
- Microphone input with listening indicator

💬 **Interview Flow**
- **Greeting**: Character greets you warmly and waits for start
- **Interview Stages**: WARM_UP → TECHNICAL → PROBLEM_SOLVING → BEHAVIORAL → STRESS
- **Closure**: Professional thank you message at the end
- **Input Control**: Smart form disabling during greeting/closure phases

🔄 **WebSocket Communication**
- Real-time bidirectional communication between frontend and backend
- Graceful error handling with soft fallback responses
- Connection status indicator

## Project structure

```
ai-interviewer/
├── backend/
│   ├── __init__.py
│   ├── interview_engine.py (Gemini API integration)
│   ├── main.py (FastAPI + WebSocket)
│   ├── requirements.txt
│   ├── system_prompt.txt
│   └── tests/
│       └── test_websocket.py
├── frontend/
│   ├── app.js (WebSocket client, STT/TTS, state management)
│   ├── avatar.js (Three.js 3D avatar rendering)
│   ├── index.html
│   ├── styles.css
│   └── tests.md
├── .env (API keys and configuration)
└── README.md
```

## Prerequisites
- Python 3.10+
- Modern browser with Web Speech API support (Chrome, Edge, Safari)
- Google Gemini API key (free tier at https://ai.google.dev)
- Default model: `gemini-2.5-flash` (best price-performance for free tier)

## Backend setup
From the project root:
```bash
cd ai-interviewer
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Create `.env` file at project root:
```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
```

Get a free Gemini API key at [https://ai.google.dev](https://ai.google.dev)

Start the server:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Or from inside backend folder:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

## Frontend setup
Serve the frontend folder (any local HTTP server):
```bash
cd frontend
python -m http.server 5500
```

Then open [http://localhost:5500](http://localhost:5500) in your browser.

The frontend automatically connects to `ws://localhost:8000/ws`.

## Using the Interview

1. **Start**: Click "Start Interview" button
2. **Avatar Greeting**: The avatar will greet you and wait
3. **Provide Answers**:
   - **Type**: Use the text input field
   - **Speak**: Click 🎤 button, speak your answer, click 🎤 again or wait for recognition to complete
4. **Interview Progression**: Answer interview questions through WARM_UP → TECHNICAL → BEHAVIORAL → STRESS phases
5. **Closing**: Avatar will thank you and close the interview
6. **End**: Click "End Interview" to stop

## Avatar States and Expressions

The avatar changes expression based on interview context:
- `smiling` - During greeting and positive interactions
- `attentive_nod` - Engaged listening
- `thinking` - Processing questions
- `confused` - Clarifying responses
- `mildly_impressed` - Positive feedback
- `neutral_disappointed` - Challenges or mistakes
- `pressure_mode` - Stress testing phase
- `concluding` - Final thank you phase

## Voice Input (Speech-to-Text)

The microphone button (🎤) uses the Web Speech API:
- Click 🎤 to start listening (button turns red with pulse animation)
- Speak clearly
- Button turns back to 🎤 when done
- Your speech is transcribed and appears in the input field
- Browser may ask for microphone permission on first use

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Avatar (Three.js) | ✅ | ✅ | ✅ | ✅ |
| TTS (Web Speech API) | ✅ | ⚠️ Limited | ✅ | ✅ |
| STT (Speech Recognition) | ✅ | ❌ | ✅ | ✅ |
| WebSocket | ✅ | ✅ | ✅ | ✅ |

Firefox has limited TTS support; consider using Chrome/Edge for best voice experience.

## Testing

### Backend WebSocket test
```bash
cd backend
pytest
```

### Frontend manual test checklist
See `frontend/tests.md` for comprehensive testing guide covering:
- Avatar rendering and animation
- Mouth and eye synchronization
- Voice input and output
- Interview flow and state transitions
- Error handling and reconnection

## Troubleshooting

**Q: Avatar doesn't appear**
- Check browser console for errors
- Verify Three.js CDN is accessible
- Try a different browser

**Q: Voice input (STT) not working**
- Chrome/Edge/Safari support it; Firefox doesn't
- Check browser microphone permissions
- Ensure HTTP or HTTPS (not file://)

**Q: Avatar lip-sync seems off**
- This is normal on first use while browser loads audio engine
- Try a different sentence
- Some browsers have speech synthesis delays

**Q: WebSocket connection refused**
- Ensure backend is running on port 8000
- Check CORS headers in main.py
- Verify firewall isn't blocking connections

**Q: Gemini API quota exceeded**
- Free tier has strict rate limits
- Wait 24 hours for quota reset (UTC midnight)
- Or obtain a new API key at https://ai.google.dev

## Architecture

**Backend** (FastAPI + Gemini):
- WebSocket endpoint at `/ws`
- Receives user text from frontend
- Sends text to Gemini via interview_engine
- Returns JSON response with system_state, avatar_state, TTS flag

**Frontend** (Vanilla JS + Three.js):
- Connects to WebSocket on load
- Captures user input (text or voice via STT)
- Sends to backend, receives AI response
- Renders avatar state changes
- Plays audio via Web Speech API (TTS)
- Updates UI with interview progress

## Future Enhancements

- Video output (face alignment, head tracking)
- Custom avatar models (ReadyPlayerMe integration)
- Interview report/scoring
- Multi-language support
- Persistence (interview history, analytics)
