# Frontend Test Checklist

## Avatar state and lip sync
- Start backend (`uvicorn backend.main:app --reload --port 8000`) and open frontend via a static server.
- Connect and trigger an AI response; confirm Web Speech API audio plays.
- Observe jaw motion while audio plays; motion stops when audio ends.
- Change `avatar_state` in a mocked payload (e.g., via console calling `handleAiMessage`) and confirm head color updates.

## Interview flow
- Click Start; connection status shows connected.
- Send a text message; it appears in the transcript and is echoed by AI response.
- Stage label updates based on `system_state` from server payloads.
- End Interview closes the socket and stops mouth animation.

## Text-only fallback
- In browser devtools, disable speech synthesis (`window.speechSynthesis.cancel()` then set `window.speechSynthesis = null`), send a new message; UI still updates and shows AI text without audio, no errors in console.
