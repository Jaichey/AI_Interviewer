# Human Observation & Behavior Analysis Extension

## Overview

The Human Observation & Behavior Analysis module is a **LOCAL-ONLY** extension to the AI Interviewer that observes and analyzes candidate behavior during interviews. It runs in parallel with the interview without interfering with existing functionality.

### Key Features

- ✅ **Face & Gaze Detection** - Tracks head direction, eye gaze, blink rate
- ✅ **Emotion Analysis** - Detects emotional states from facial expressions
- ✅ **Voice Stress Detection** - Analyzes pitch, energy, and speaking patterns
- ✅ **Non-Intrusive Pacing** - Adjusts interview pace based on candidate behavior
- ✅ **Behavioral Logging** - Tracks all observations throughout interview
- ✅ **Final Report** - Generates comprehensive behavioral analysis after interview

### No Cloud Dependencies

- ✅ **100% Local Processing** - All analysis happens on the local machine
- ✅ **No Cloud APIs** - No internet calls required
- ✅ **No Data Transmission** - All data stays local
- ✅ **Privacy First** - Camera and audio only used for analysis

---

## Architecture

### Backend Modules

#### 1. `face_analyzer.py`
Detects and analyzes facial features using MediaPipe Face Mesh.

**Detects:**
- Face presence
- Head direction (yaw, pitch)
- Eye gaze direction (left, right, center)
- Blink rate
- Looking away incidents

**Usage:**
```python
from face_analyzer import FaceAnalyzer

analyzer = FaceAnalyzer()
frame = cv2.imread("image.jpg")
result = analyzer.analyze(frame)
# Returns: face_detected, head_yaw, head_pitch, gaze_direction, blink_count, etc.
```

#### 2. `emotion_analyzer.py`
Analyzes facial expressions to detect emotional states.

**Detects:**
- Neutral, Happy, Focused, Stressed, Confused, Confident
- Confidence scores for each emotion
- Overall stress level

**Usage:**
```python
from emotion_analyzer import EmotionAnalyzer

analyzer = EmotionAnalyzer()
frame = cv2.imread("image.jpg")
result = analyzer.analyze(frame)
# Returns: emotion, confidence, emotion_scores, stress_level
```

#### 3. `audio_analyzer.py`
Analyzes microphone audio for stress indicators.

**Analyzes:**
- Fundamental frequency (pitch)
- Energy (RMS)
- Speaking rate
- Silence duration
- Pitch spikes (stress indicators)
- Voice confidence score

**Usage:**
```python
from audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer()
analyzer.add_audio_chunk(audio_np_array)
result = analyzer.analyze()
# Returns: pitch, energy, speaking_rate, silence_duration, stress_level, voice_confidence
```

#### 4. `observation_logger.py`
Logs all observations and generates final behavioral report.

**Tracks:**
- Eye contact periods
- Stress timeline
- Voice confidence trajectory
- Emotional expressions
- Interview violations

**Final Report Includes:**
```json
{
  "eye_contact_score": 0-10,
  "focus_score": 0-10,
  "stress_level": "low|medium|high",
  "voice_confidence": 0-10,
  "violations": {...},
  "behavioral_strengths": [...],
  "behavioral_improvements": [...],
  "overall_interview_readiness": "low|medium|high"
}
```

#### 5. `human_observation_engine.py`
Main observation engine that coordinates all analyzers.

**Responsibilities:**
- Manages camera and microphone access
- Runs observation in separate thread (non-blocking)
- Coordinates all analyzers
- Manages logging
- Controls interview pace

**Usage:**
```python
from human_observation_engine import HumanObservationEngine

engine = HumanObservationEngine()
engine.start()  # Start observing
# ... interview happens ...
report = engine.generate_report()
engine.stop()
```

### Frontend Integration

#### `observation_client.js`
JavaScript client for communicating with observation backend.

**Methods:**
```javascript
import { ObservationClient } from './observation_client.js';

const client = new ObservationClient();

// Lifecycle
await client.startObservation();  // Start camera + analysis
await client.stopObservation();   // Stop and cleanup

// Polling
client.startPolling(500);  // Poll every 500ms
client.onObservation = (obs) => { /* handle observation */ };
client.stopPolling();

// Reports
const obs = await client.getLatestObservation();
const report = await client.getReport();

// Reset
await client.reset();
```

#### UI Components
- **Camera Panel** - Shows candidate's webcam feed
- **Observation Metrics** - Real-time display of:
  - Eye Contact Score (0-10)
  - Focus Score (0-10)
  - Stress Level (low|medium|high)
  - Voice Confidence (0-10)

---

## Backend API Endpoints

### POST `/observation/start`
Starts the observation engine (camera + audio monitoring).

**Response:**
```json
{
  "success": true,
  "message": "Observation engine started"
}
```

### POST `/observation/stop`
Stops the observation engine.

**Response:**
```json
{
  "success": true,
  "message": "Observation engine stopped"
}
```

### POST `/observation/add_audio`
Adds audio frame for analysis (base64 encoded).

**Request:**
```json
{
  "audio_data": "base64_encoded_audio"
}
```

**Response:**
```json
{
  "success": true
}
```

### GET `/observation/latest`
Gets the latest behavioral observation.

**Response:**
```json
{
  "success": true,
  "observation": {
    "timestamp": 12.345,
    "face": {...},
    "emotion": {...},
    "audio": {...},
    "pace_adjustment": {...}
  }
}
```

### GET `/observation/report`
Gets final behavioral analysis report.

**Response:**
```json
{
  "success": true,
  "report": {
    "eye_contact_score": 7,
    "focus_score": 8,
    "stress_level": "low",
    "voice_confidence": 7.5,
    ...
  }
}
```

### POST `/observation/reset`
Resets observation engine for new interview.

**Response:**
```json
{
  "success": true,
  "message": "Observation engine reset"
}
```

---

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `opencv-python` - Camera capture and image processing
- `mediapipe` - Face detection and landmark tracking
- `numpy` - Numerical computation

### 2. Verify Installation

```bash
python -c "import cv2; import mediapipe; print('OK')"
```

---

## Usage Flow

### 1. Start Interview
```javascript
// Frontend automatically:
// 1. Connects to WebSocket
// 2. Calls observation.startObservation()
// 3. Starts polling for observations every 500ms
// 4. Displays candidate camera feed
```

### 2. During Interview
```
Observation Engine (parallel thread)
├── Capture webcam frame (15 FPS)
├── Analyze face/gaze
├── Analyze emotion
├── Analyze accumulated audio
├── Calculate pace adjustments
└── Log everything

Frontend (every 500ms)
├── Fetch latest observation
├── Update metrics display
└── Check for pace adjustments
```

### 3. Interview Ends
```javascript
// Frontend automatically:
// 1. Calls observation.stopObservation()
// 2. Stops polling
// 3. Fetches final report
// 4. Displays behavioral analysis
```

---

## Configuration

### Face Analyzer

Adjustable thresholds in `face_analyzer.py`:
```python
self.eye_aspect_ratio_threshold = 0.2  # Blink detection
```

### Audio Analyzer

Adjustable thresholds in `audio_analyzer.py`:
```python
SAMPLE_RATE = 16000  # Audio sample rate
CHUNK_SIZE = 2048    # Audio chunk size
```

### Pace Controller

Adjustable thresholds in `human_observation_engine.py`:
```python
STRESS_THRESHOLD = 0.6        # High stress detection
LOOKING_AWAY_THRESHOLD = 5    # seconds
SILENCE_THRESHOLD = 3         # seconds
```

---

## Performance Considerations

### CPU Usage
- Face detection: ~20-30% on modern CPU
- Emotion detection: ~5-10%
- Audio analysis: <1%
- **Total:** ~30-40% on mid-range CPU

### Memory Usage
- Face analyzer: ~100MB
- Emotion analyzer: ~50MB
- Audio buffer (2 sec): ~64KB
- **Total:** ~200MB

### Optimization Tips

1. **Lower Camera FPS**
   ```python
   engine.cap.set(cv2.CAP_PROP_FPS, 10)  # Default: 15
   ```

2. **Disable Emotion Analysis** (if needed)
   ```python
   # Comment out in observation loop
   emotion_data = self.emotion_analyzer.analyze(frame)
   ```

3. **Reduce Polling Frequency**
   ```javascript
   observation.startPolling(1000);  // Every 1000ms instead of 500ms
   ```

---

## Data Flow Diagram

```
Webcam              Microphone
  │                   │
  └──→ Face Analyzer  │
  │    │              │
  │    └──→ Emotion   │
  │         Analyzer  │
  │         │         │
  └─────────┴──────→ Audio Analyzer
            │
            └──→ Observation Logger
                │
                ├──→ Pace Controller
                │
                └──→ Observation Queue
                     │
                     └──→ Frontend (polling)
```

---

## Violation Detection

The system detects and logs the following interview violations:

| Violation | Threshold | Impact |
|-----------|-----------|--------|
| Looking Away | > 25° head yaw, > 20° pitch | Focus score ↓ |
| High Stress | Pitch/energy spike | Stress level ↑ |
| Long Silence | > 3 seconds | Interview pacing adjusted |
| Face Not Detected | Face out of frame | Eye contact score ↓ |

---

## Behavioral Report

### Example Report Output

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
• Increase eye contact - avoid looking away during responses
• Build voice confidence - practice public speaking

Overall Interview Readiness: high

Session Duration: 300s
```

---

## Troubleshooting

### Camera Not Detected
```python
# Check available cameras
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())  # Should be True
```

### High CPU Usage
- Reduce camera FPS
- Disable emotion detection
- Increase polling interval

### Poor Face Detection
- Ensure good lighting
- Camera should show full face
- Avoid extreme angles

### Silence Detection Not Working
- Check microphone is active
- Ensure audio level is adequate
- Verify backend is receiving audio frames

---

## Testing

### Manual Test

```python
from human_observation_engine import HumanObservationEngine

engine = HumanObservationEngine()
engine.start()

# Simulate interview (10 seconds)
import time
time.sleep(10)

# Get observations
for i in range(10):
    obs = engine.observation_queue.get()
    print(f"Observation {i}:")
    print(f"  Face detected: {obs['face']['face_detected']}")
    print(f"  Emotion: {obs['emotion']['emotion']}")
    print(f"  Stress: {obs['audio']['stress_level']}")

engine.stop()
report = engine.generate_report()
print(report.to_json())
```

---

## Privacy & Security

### Data Handling
- ✅ All processing local only
- ✅ No data sent to servers
- ✅ No recording (unless explicitly enabled)
- ✅ No permanent storage
- ✅ Camera/audio cleared after interview

### User Consent
- Camera access requires explicit user permission
- Observation can be toggled on/off
- Final report is shown to candidate

---

## Future Enhancements

Possible extensions (not implemented):
- [ ] Head movement tracking (nodding, shaking)
- [ ] Lip reading for stress indicators
- [ ] Fidgeting detection
- [ ] Eye contact duration histogram
- [ ] Emotional state transitions
- [ ] Speaking fluency metrics
- [ ] Background distraction detection
- [ ] Posture analysis

---

## Compliance

This observation system is designed for:
- ✅ Interview coaching
- ✅ Behavioral analysis
- ✅ Performance feedback
- ✅ Candidate development

**Not designed for:**
- ❌ Biometric authentication
- ❌ Surveillance
- ❌ Discriminatory evaluation
- ❌ Privacy violation

---

## Support

For issues or questions:
1. Check logs in console
2. Enable debug mode: `[DEBUG]` logs in console
3. Verify camera/microphone permissions
4. Check backend is running on port 8000

---

## License

Part of AI Interviewer project. See main LICENSE file.
