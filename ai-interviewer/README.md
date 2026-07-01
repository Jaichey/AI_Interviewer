# 🎯 HireSense AI - Research-Grade AI Interview Platform

> **Advanced AI-Powered Interview System with Real-Time Proctoring, Gaze Tracking, and Behavioral Analysis**

HireSense AI is a production-ready, research-grade interview platform that combines advanced proctoring capabilities with AI-driven interviews. Built for both real-world deployment and academic research, it provides comprehensive behavioral analytics, eye tracking, emotion detection, and violation monitoring.

---

## 🌟 Key Features

### 🎥 **Advanced Proctoring System**
- **Real Eye Tracking** - Iris landmark-based gaze estimation
- **Multi-Person Detection** - YOLOv8-powered person counting
- **Gaze Direction Classification** - CENTER / LEFT / RIGHT / UP / DOWN
- **Blink Detection** - Eye Aspect Ratio (EAR) based monitoring
- **Head Pose Estimation** - Pitch, Yaw, Roll calculations
- **Look-Away Duration Tracking** - Real-time monitoring

### 🧠 **Behavioral Analysis**
- **Emotion Recognition** - DeepFace-powered emotion detection
- **Voice Stress Analysis** - Real-time stress level monitoring
- **Confidence Scoring** - Multi-metric confidence assessment
- **Engagement Tracking** - Continuous engagement monitoring

### 📊 **Dataset Generation**
- **Structured Logging** - Per-frame metrics, transcripts, violations
- **Synthetic Data Mode** - 100+ realistic synthetic interview sessions
- **Real Data Mode** - Live session recording and logging
- **Auto-Scoring System** - Deterministic scoring algorithm

### 💻 **Modern UI**
- **Real-Time Dashboard** - Live proctoring metrics display
- **Three.js Avatar** - ReadyPlayerMe integration
- **WebRTC Camera Preview** - Browser-based webcam access
- **Toast Notifications** - Non-intrusive warning system

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome/Firefox/Edge recommended)
- Webcam and microphone
- 4GB+ RAM recommended

### Option 1: Automated Setup (Recommended)

**Windows:**
```powershell
.\scripts\setup_models_windows.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/setup_models_linux.sh
./scripts/setup_models_linux.sh
```

This will:
- ✅ Install all Python dependencies
- ✅ Download YOLOv8 model weights
- ✅ Install MediaPipe, DeepFace, OpenCV
- ✅ Generate synthetic dataset (100 sessions)

### Option 2: Manual Setup

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Download YOLOv8 model
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
mv yolov8s.pt backend/yolov8s.pt

# Generate synthetic dataset
python backend/synthetic_data_generator.py --num-sessions 100
```

---

## ⚡ Quick Start

### 1. Start the Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will start at: `http://localhost:8000`

### 2. Open the Frontend

Open `frontend/index.html` in your browser or serve it:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 8080
```

Frontend will be at: `http://localhost:8080`

### 3. Start Interview

1. **Allow camera/microphone** access when prompted
2. **Select subject** (e.g., "Python", "System Design")
3. **Select company** (e.g., "Google", "Startup")
4. Click **"Start Interview"**
5. Answer questions via **text** or **voice** (click 🎤)

### 4. Monitor Proctoring Dashboard

The **HireSense Proctoring Dashboard** (top-right) displays:
- ✅ Eye Contact Percentage
- 📍 Gaze Direction
- 🔄 Head Pose (Yaw/Pitch)
- 👁️ Blink Rate
- 😊 Emotion
- 📈 Stress Level
- 👥 Person Count
- ⚠️ Warnings
- 🔍 Suspicious Score

---

## 🏗️ Architecture

### Backend Stack
```
FastAPI + WebSocket
├── main.py                          # API endpoints, WebSocket server
├── interview_engine.py               # AI interview logic (Gemini/OpenAI)
├── human_observation_engine.py       # Observation orchestration
├── face_analyzer.py                  # Gaze tracking, head pose, blink detection
├── emotion_analyzer.py               # DeepFace emotion recognition
├── audio_analyzer.py                 # Voice stress analysis
├── observation_logger.py             # Dataset logging and report generation
├── synthetic_data_generator.py       # Synthetic dataset creation
└── auto_score_generator.py           # Automated scoring system
```

### Frontend Stack
```
Vanilla JS + Three.js
├── index.html                        # Main UI layout
├── app.js                            # Interview logic, WebSocket client
├── observation_client.js             # Observation polling, video capture
├── avatar.js                         # Three.js avatar management
└── styles.css                        # Modern UI styling
```

---

## 📁 Dataset Structure

```
dataset/
├── sessions/                # Real interview sessions
│   └── session_<uuid>/
│       ├── video_metadata.json
│       ├── transcript.json
│       ├── gaze_metrics.json
│       ├── emotion_metrics.json
│       ├── proctoring_metrics.json
│       └── final_report.json
│
└── synthetic/               # Synthetic dataset
    ├── index.json
    └── session_<uuid>/
        └── [same structure as above]
```

---

## ⚙️ Configuration

Edit `config.json` to customize behavior:

```json
{
  "DATA_MODE": "synthetic",              // "synthetic" or "real"
  "DATASET_PATH": "dataset",
  "PROCTORING": {
    "multi_person_threshold_seconds": 3,
    "look_away_threshold_seconds": 10,
    "warning_limit": 3,
    "enable_violations": true
  },
  "GAZE_TRACKING": {
    "enable_iris_tracking": true,
    "enable_head_pose": true,
    "enable_blink_detection": true
  }
}
```

### Switching Modes

**Synthetic Mode** (for testing/development):
```json
"DATA_MODE": "synthetic"
```

**Real Mode** (for production):
```json
"DATA_MODE": "real"
```

---

## 🔌 API Reference

### WebSocket Endpoint

**Endpoint:** `ws://localhost:8000/ws`

**Message Format:**
```json
{
  "text": "User's answer to interview question"
}
```

**Response Format:**
```json
{
  "system_state": "TECHNICAL",
  "interviewer_response": "AI's response",
  "avatar_state": "neutral_listening",
  "tts_enabled": true
}
```

### REST Endpoints

#### `GET /observation/latest`
Get latest behavioral observation with warnings

**Response:**
```json
{
  "success": true,
  "observation": {
    "timestamp": 123.45,
    "face": {
      "face_detected": true,
      "eye_contact_confidence": 0.85,
      "gaze_direction": "center",
      "head_yaw": -2.5,
      "head_pitch": 3.1,
      "blink_count": 45
    },
    "emotion": {
      "emotion": "confident",
      "confidence": 0.87
    },
    "audio": {
      "stress_level": "low",
      "voice_confidence": 7.5
    }
  },
  "warnings": []
}
```

#### `GET /report/{session_id}`
Get final report for specific session

---

## 🧪 Development

### Generate Synthetic Dataset

```bash
python backend/synthetic_data_generator.py --num-sessions 100
```

### Auto-Score Sessions

```bash
# Score single session
python backend/auto_score_generator.py --session-dir dataset/sessions/session_abc123

# Score entire dataset
python backend/auto_score_generator.py --dataset-dir dataset/synthetic
```

---

## 🔬 Research Usage

### Dataset Export

Export dataset for research analysis:

```python
import json
from pathlib import Path

def export_dataset(dataset_dir):
    """Export all sessions for analysis."""
    sessions = []
    for session_dir in Path(dataset_dir).glob("session_*/"):
        report_file = session_dir / "final_report.json"
        if report_file.exists():
            with open(report_file) as f:
                sessions.append(json.load(f))
    return sessions

sessions = export_dataset("dataset/synthetic")
print(f"Exported {len(sessions)} sessions")
```

### Metrics for Analysis

**Gaze Metrics:**
- Eye contact percentage
- Gaze direction distribution
- Look-away frequency and duration
- Blink rate

**Behavioral Metrics:**
- Emotion distribution
- Stress levels
- Voice confidence
- Head movement patterns

**Performance Metrics:**
- Technical scores
- Communication scores
- Overall interview performance
- Hire/reject decisions

---

## 🐛 Troubleshooting

### Issue: Camera not working

**Solution:**
- Ensure browser has camera permissions
- Check if another app is using the camera
- Try different browser (Chrome recommended)

### Issue: YOLOv8 model not found

**Solution:**
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
mv yolov8s.pt backend/yolov8s.pt
```

### Issue: High CPU usage

**Solution:**
- Reduce video frame capture rate in `observation_client.js`:
  ```javascript
  setTimeout(captureFrame, 500); // Lower to 2 FPS
  ```

### Issue: WebSocket connection refused

**Solution:**
- Ensure backend is running: `uvicorn main:app --reload`
- Check CORS settings in `main.py`
- Verify firewall settings

---

## 📝 License

This project is licensed under the MIT License.

---

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced emotion recognition models
- [ ] Real-time interview coaching
- [ ] Integration with ATS systems
- [ ] Mobile app support
- [ ] Advanced analytics dashboard

---

**Built with ❤️ for the future of AI-powered interviews**
