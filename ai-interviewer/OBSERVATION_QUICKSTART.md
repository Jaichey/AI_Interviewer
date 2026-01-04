# Human Observation Module - Quick Start Guide

## What's New

The AI Interviewer now includes a **Local Behavioral Observation System** that:

- 📹 **Observes candidate via webcam** - Face detection, gaze tracking, blink rate
- 🎤 **Analyzes voice** - Stress detection, pitch analysis, speaking patterns
- 😊 **Detects emotions** - Neutral, stressed, confident, confused, etc.
- 🔄 **Adjusts pace** - Non-intrusively delays questions if candidate is stressed
- 📊 **Generates report** - Behavioral analysis after interview ends

**IMPORTANT: Everything is LOCAL - No cloud APIs, no data sent anywhere.**

---

## Installation

### 1. Install New Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `opencv-python` - Camera access and image processing
- `mediapipe` - Face detection
- `numpy` - Numerical computation

### 2. Verify Installation

```bash
python test_observation_integration.py
```

You should see:
```
✓ FaceAnalyzer imported
✓ EmotionAnalyzer imported
✓ AudioAnalyzer imported
✓ ObservationLogger imported
✓ HumanObservationEngine imported
✓ ALL TESTS PASSED
```

---

## Running

### Terminal 1: Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Start Frontend

```bash
cd frontend
python -m http.server 5500
```

Expected output:
```
Serving HTTP on 0.0.0.0 port 5500
```

### Terminal 3: Open Browser

```
http://localhost:5500
```

---

## Using the Observation Feature

### 1. Start Interview
- Click **Start Interview** button
- Backend automatically starts observation engine
- Camera access will be requested (allow it!)

### 2. View Candidate Feed
- Click **📹** button to toggle candidate camera panel
- Shows live webcam feed

### 3. Real-Time Metrics
Below camera feed, you see:
- **Eye Contact:** 0-10 score
- **Focus:** 0-10 score
- **Stress:** low | medium | high
- **Voice:** 0-10 confidence score

These update in real-time as interview progresses.

### 4. Behavioral Signals
System sends subtle signals based on observations:
- ✓ High stress detected → Delays next question by 2 seconds
- ✓ Looking away frequently → Increases pause tolerance
- ✓ Long silence → Allows more thinking time

**No interruptions or jarring notifications** - all adjustments are seamless.

### 5. End Interview
When interview ends, you see:

```
📊 **BEHAVIORAL ANALYSIS REPORT**

Eye Contact Score: 7/10
Focus Score: 8/10
Stress Level: low
Voice Confidence: 7.5/10

Strengths:
• Good eye contact maintained throughout interview
• Confident and clear voice projection
• Excellent focus and attention to interviewer

Areas for Improvement:
• Build voice confidence - practice public speaking

Overall Interview Readiness: high

Session Duration: 300s
```

---

## Architecture

```
Webcam → FaceAnalyzer → Gaze, Head Direction, Blinks
Microphone → AudioAnalyzer → Pitch, Energy, Stress
Both → EmotionAnalyzer → Confidence, Stress Level
All → ObservationLogger → Violations, Trends
All → PaceController → Interview Adjustments
All → Frontend → Display Metrics + Final Report
```

All analysis happens **locally on your machine** - no data leaves!

---

## Configuration

Edit `backend/observation_config.py` to adjust:

```python
# Camera settings
CAMERA_FPS = 15  # Lower = less CPU usage

# Face detection
YAW_LOOKING_AWAY_THRESHOLD = 25  # degrees
PITCH_LOOKING_AWAY_THRESHOLD = 20  # degrees

# Stress detection
PITCH_DEVIATION_HIGH_STRESS = 0.3
ENERGY_DEVIATION_HIGH_STRESS = 0.4

# Pace adjustments
STRESS_DELAY = 2  # seconds
SILENCE_THRESHOLD = 3  # seconds

# And more...
```

---

## Troubleshooting

### Camera Not Working
```python
# Check if camera is available
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())  # Should be True
```

### High CPU Usage
- Reduce `CAMERA_FPS` in observation_config.py
- Disable emotion detection if not needed
- Increase polling interval (less frequent updates)

### Missing Face Detection
- Ensure good lighting
- Position yourself centered in frame
- Avoid extreme angles or occlusions

### Poor Stress Detection
- Ensure microphone is working
- Check audio levels
- Make sure audio is being captured

### Observation Not Starting
- Check backend logs for errors
- Verify camera permissions granted
- Check browser console for errors

---

## API Endpoints (Advanced)

If you want to integrate with other systems:

```bash
# Start observation
POST http://localhost:8000/observation/start

# Get latest observation
GET http://localhost:8000/observation/latest

# Get final report
GET http://localhost:8000/observation/report

# Stop observation
POST http://localhost:8000/observation/stop

# Reset for new interview
POST http://localhost:8000/observation/reset
```

Example response from `/observation/latest`:
```json
{
  "success": true,
  "observation": {
    "timestamp": 12.345,
    "face": {
      "face_detected": true,
      "head_yaw": 5.2,
      "head_pitch": -2.1,
      "looking_away": false,
      "blink_count": 8,
      "gaze_direction": "center"
    },
    "emotion": {
      "emotion": "Neutral",
      "confidence": 0.7,
      "stress_level": "low"
    },
    "audio": {
      "pitch": 120.5,
      "stress_level": "low",
      "voice_confidence": 7.5,
      "silence_detected": false
    },
    "pace_adjustment": {
      "delay_next_question": 0,
      "reduce_pressure": false
    }
  }
}
```

---

## Privacy & Data

✅ **100% Local Processing**
- No cloud calls
- No data transmission
- No internet required
- All analysis on your machine

✅ **No Recording**
- Camera/audio used only for analysis
- Nothing saved to disk (unless you explicitly export)
- Cleared after interview

✅ **User Control**
- Camera feed can be hidden
- Can disable observation anytime
- Final report is just feedback

---

## File Structure

```
backend/
├── human_observation_engine.py    # Main engine
├── face_analyzer.py               # Face detection
├── emotion_analyzer.py            # Emotion detection
├── audio_analyzer.py              # Audio analysis
├── observation_logger.py          # Logging & reports
├── observation_config.py          # Configuration
├── test_observation_integration.py # Test suite
└── requirements.txt               # Dependencies

frontend/
├── observation_client.js          # JavaScript client
├── app.js                         # Main app (updated)
├── index.html                     # HTML (updated)
└── styles.css                     # Styles (updated)

docs/
└── OBSERVATION_MODULE.md          # Detailed documentation
```

---

## Performance

### CPU Usage
- Low: ~10-20% (camera only)
- Medium: ~30-40% (camera + audio)
- Peak: ~50% (camera + audio + emotion)

### Memory
- ~200MB total (face detector + emotion + buffers)

### Network
- **ZERO** - Everything local!

---

## Known Limitations

1. **Lighting Matters** - Face detection works best in good lighting
2. **Camera Angle** - Full face must be visible
3. **One Face** - Only detects first face in frame
4. **Pitch Estimation** - Simplified, works ~80% of time
5. **Emotion Detection** - Heuristic-based (no ML model yet)

---

## Future Enhancements

Possible additions:
- Head nodding/shaking detection
- Posture analysis
- Eye contact duration histogram
- Speaking fluency metrics
- Emotional state transitions
- Fidgeting detection

---

## Support

### Debug Mode
Console shows detailed logs:
```javascript
[DEBUG] Speech recognition started
[DEBUG] Observation engine started
[DEBUG] 3-second pause detected, sending: ...
```

### Check Logs
- Browser console: `F12` → Console tab
- Backend console: Check uvicorn output

### Test Offline
```bash
cd backend
python test_observation_integration.py
```

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Test integration: `python test_observation_integration.py`
3. ✅ Start backend: `uvicorn main:app --reload --port 8000`
4. ✅ Start frontend: `python -m http.server 5500`
5. ✅ Open browser: `http://localhost:5500`
6. ✅ Click camera button to view feed
7. ✅ Start interview and observe metrics!

---

## Questions?

Check the detailed documentation: [OBSERVATION_MODULE.md](./OBSERVATION_MODULE.md)

Or review the code - it's well-commented!

Happy interviewing! 🚀
