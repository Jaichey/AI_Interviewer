# AI Interviewer - Project Overview

## 📋 Table of Contents
- [Introduction](#introduction)
- [Application Purpose](#application-purpose)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [AI Models & APIs](#ai-models--apis)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [System Workflow](#system-workflow)
- [Installation & Setup](#installation--setup)
- [Browser Compatibility](#browser-compatibility)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Introduction

**AI Interviewer** is an enterprise-grade, intelligent interview simulation platform that leverages cutting-edge AI technologies to conduct realistic technical interviews. The application features real-time behavioral monitoring, 3D avatar interaction, voice capabilities, and comprehensive interview assessment through multiple AI models.

---

## 🚀 Application Purpose

The AI Interviewer serves multiple critical purposes:

### **For Job Seekers**
- Practice technical interviews in a realistic, pressure-free environment
- Receive immediate feedback on communication and behavioral aspects
- Experience various interview stages: warm-up, technical, problem-solving, behavioral, and stress testing
- Improve interview skills through structured practice sessions

### **For Organizations**
- Standardized interview process with consistent questioning
- Real-time behavioral analysis and proctoring capabilities
- Automated candidate assessment and scoring
- Multi-interviewer simulation for panel interview preparation
- Subject-specific and company-specific interview customization

### **For Educational Institutions**
- Training students for campus placements
- Assessment of communication and problem-solving skills
- Performance analytics and improvement tracking
- Safe learning environment with no real-world consequences

---

## ✨ Key Features

### 1. **Realistic 3D Avatar System**
- **Human-like 3D avatars** powered by Ready Player Me models
- **Facial expressions**: Smiling, thinking, listening, confused, impressed, disappointed, pressure mode
- **Natural animations**: Blinking (3-7 second intervals), mouth movements synced with speech
- **Head movements**: Nodding, idle movements for realistic presence
- **Multi-avatar support**: Up to 3 different avatars for multi-interviewer simulation

### 2. **Voice Interaction**
- **Text-to-Speech (TTS)**: Avatar speaks AI responses using Web Speech API
- **Speech-to-Text (STT)**: Voice input for candidate responses via microphone
- **Natural speech synthesis** with proper pacing and intonation
- **Audio analysis**: Voice stress detection, speaking patterns, silence detection

### 3. **Behavioral Observation & Proctoring**
- **Real-time monitoring** of candidate behavior during interview
- **Face detection**: Multiple person detection, face visibility tracking
- **Eye tracking**: Eye contact confidence, looking away detection, gaze direction
- **Emotion analysis**: 7 emotional states (neutral, happy, sad, angry, surprised, fear, disgust)
- **Audio stress analysis**: Voice stress levels, speaking pace, confidence detection
- **Violation detection**: Automatic termination on proctoring violations
- **100% Local Processing**: No cloud upload, privacy-first approach

### 4. **Intelligent Interview Flow**
- **Structured stages**: GREETING → WARM_UP → TECHNICAL → PROBLEM_SOLVING → BEHAVIORAL → STRESS → CLOSURE
- **Context-aware questioning**: Questions adapt based on previous answers
- **Subject specialization**: DAA, OS, CN, SE, WEB, DBMS, OOPS, System Design
- **Company-specific**: Tailored questions for Google, Amazon, Meta, Microsoft, Apple, Netflix, Startups
- **Dynamic pace control**: Adjusts based on stress signals and candidate behavior

### 5. **Real-time Communication**
- **WebSocket-based** bidirectional communication
- **Sub-second latency** for interactive conversation
- **Connection status monitoring** with graceful reconnection
- **Error handling**: Soft fallback responses when connection issues occur

### 6. **Professional UI/UX**
- **Clean, modern interface** with professional minimal design
- **Live camera feed**: Candidate video display with speaking indicators
- **Interview controls**: Start, end, continuous mode toggles
- **Stage progression display**: Visual feedback on interview phase
- **Warning system**: Real-time behavioral warnings and notifications
- **Toast notifications**: Non-intrusive feedback messages

---

## 🛠️ Technology Stack

### **Backend Technologies**
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.10+ | Primary backend language |
| **FastAPI** | 0.115.0 | Modern async web framework |
| **Uvicorn** | 0.30.1 | ASGI server for FastAPI |
| **WebSockets** | 12.0 | Real-time bidirectional communication |
| **Python-dotenv** | 1.0.1 | Environment variable management |
| **OpenCV** | 4.8.0+ | Computer vision and video processing |
| **MediaPipe** | 0.10.30+ | Face detection and landmark tracking |
| **NumPy** | 1.26.0+ | Numerical computing for ML operations |
| **PyTest** | 8.3.3 | Testing framework |
| **HTTPX** | 0.27.2 | Async HTTP client for API calls |

### **Frontend Technologies**
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Vanilla JavaScript** | ES6+ | Core application logic |
| **Three.js** | 0.158.0 | 3D avatar rendering and animation |
| **GLTFLoader** | - | Loading 3D avatar models |
| **Web Speech API** | Native | Text-to-Speech and Speech-to-Text |
| **WebSocket API** | Native | Real-time server communication |
| **WebRTC** | Native | Camera and microphone access |
| **HTML5** | - | Structure and layout |
| **CSS3** | - | Modern styling with animations |

### **Infrastructure**
- **CORS**: Cross-Origin Resource Sharing enabled
- **ASGI**: Asynchronous Server Gateway Interface
- **Threading**: Multi-threaded observation engine
- **Queue-based processing**: Non-blocking behavioral analysis

---

## 🤖 AI Models & APIs

### **1. Google Gemini AI (Primary)**
The application uses Google's Gemini models with intelligent rotation:

| Model | Daily Limit | RPM | Use Case |
|-------|-------------|-----|----------|
| **gemini-2.5-flash** | 1,500 | 15 | Primary model - Best price/performance |
| **gemini-2.5-flash-lite** | 2,000 | 20 | Fallback when flash quota exceeded |
| **gemini-2.5-pro** | 50 | 2 | High-quality responses for complex scenarios |

**Features:**
- Automatic model rotation when quotas reached
- Rate limiting (RPM tracking)
- JSON response formatting
- Streaming support for real-time responses

### **2. Fallback AI Providers**
The system implements a cascade fallback strategy:

1. **Groq** (openai/gpt-oss-120b)
2. **OpenRouter** (deepseek/deepseek-r1-0528:free)
3. **Hugging Face** (tiiuae/falcon-7b-instruct)
4. **Cohere** (command-r)

### **3. Computer Vision Models**

#### **YOLOv8 (Ultralytics)**
- **Model**: YOLOv8s (Small variant)
- **Purpose**: Robust multi-person detection for proctoring
- **Accuracy**: High precision person counting
- **Speed**: Real-time processing (30+ FPS)
- **File**: `yolov8s.pt` (11 MB)

#### **MediaPipe Face Mesh**
- **Provider**: Google MediaPipe
- **Purpose**: 468 facial landmarks + iris tracking
- **Features**: 
  - Face detection and tracking
  - Eye gaze estimation
  - Head pose estimation
  - Blink detection
  - Expression analysis

#### **OpenCV Haar Cascades**
- **Purpose**: Fallback face detection
- **Model**: `haarcascade_frontalface_default.xml`
- **Used**: Only when MediaPipe/YOLO unavailable

### **4. Audio Analysis Models**

#### **Librosa (Audio Processing)**
- **Purpose**: Voice feature extraction
- **Features**: Pitch, energy, spectral features
- **Stress Detection**: Analyzes voice stress patterns

#### **Custom Emotion Detection**
- **Framework**: Custom neural network with MediaPipe
- **Emotions**: 7 states (neutral, happy, sad, angry, surprised, fear, disgust)
- **Accuracy**: Real-time emotion classification

---

## 🏗️ Architecture

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │  3D Avatar │  │  WebSocket  │  │  Voice Input/Output  │ │
│  │  (Three.js)│  │   Client    │  │  (Web Speech API)    │ │
│  └────────────┘  └─────────────┘  └──────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Camera & Audio Capture (WebRTC)               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ WebSocket (ws://localhost:8000/ws)
                             │ HTTP (API Calls)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                          BACKEND                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI + WebSocket Server              │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                               │
│       ┌─────────────────────┼─────────────────────┐         │
│       ▼                     ▼                     ▼         │
│  ┌──────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ Interview│      │ Observation  │      │  AI Provider │  │
│  │  Engine  │      │   Engine     │      │   Manager    │  │
│  └──────────┘      └──────────────┘      └──────────────┘  │
│       │                    │                     │          │
│       │                    ▼                     │          │
│       │         ┌──────────────────────┐         │          │
│       │         │  Face Analyzer       │         │          │
│       │         │  (MediaPipe+YOLO)    │         │          │
│       │         └──────────────────────┘         │          │
│       │         ┌──────────────────────┐         │          │
│       │         │  Emotion Analyzer    │         │          │
│       │         │  (Custom Model)      │         │          │
│       │         └──────────────────────┘         │          │
│       │         ┌──────────────────────┐         │          │
│       │         │  Audio Analyzer      │         │          │
│       │         │  (Librosa)           │         │          │
│       │         └──────────────────────┘         │          │
│       │                                          │          │
│       └──────────────────┬───────────────────────┘          │
│                          ▼                                  │
│              ┌──────────────────────┐                       │
│              │   Gemini API         │                       │
│              │   (+ Fallbacks)      │                       │
│              └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow**

1. **User Input** → Frontend captures text/voice
2. **WebSocket** → Sends to backend `/ws` endpoint
3. **Interview Engine** → Processes with conversation history
4. **AI API Call** → Gemini generates response (with fallback cascade)
5. **Observation Engine** → Analyzes video/audio in parallel thread
6. **Response** → Backend sends JSON response to frontend
7. **Avatar + TTS** → Frontend renders response and speaks
8. **Behavioral Warnings** → Real-time proctoring feedback

---

## 🧩 Core Components

### **Backend Components**

#### **1. main.py**
- FastAPI application initialization
- WebSocket endpoint `/ws` for real-time communication
- REST endpoints for observation (`/observation/*`)
- CORS middleware configuration
- Health check endpoint (`/health`)

#### **2. interview_engine.py**
- **InterviewEngine**: Main AI orchestration class
- **ModelRotator**: Intelligent model switching based on quotas
- **Provider Cascade**: Automatic fallback through 5+ AI providers
- **JSON Response Parser**: Ensures structured output
- **Rate Limiting**: RPM tracking per model

#### **3. human_observation_engine.py**
- **HumanObservationEngine**: Master observation coordinator
- **PaceController**: Adjusts interview pace based on stress
- **Threading**: Non-blocking observation loop
- **Queue Management**: Video/audio frame buffering
- **Report Generation**: Final behavioral analysis

#### **4. face_analyzer.py**
- **YOLOv8 Integration**: Multi-person detection
- **MediaPipe Face Mesh**: 468 facial landmarks
- **Eye Tracking**: Iris-based gaze estimation
- **Head Pose**: 3D pose estimation
- **Blink Detection**: Eye aspect ratio calculation

#### **5. emotion_analyzer.py**
- 7-emotion classification (neutral, happy, sad, angry, surprised, fear, disgust)
- Expression strength calculation
- Temporal smoothing for stable detection

#### **6. audio_analyzer.py**
- Voice stress level detection (low, medium, high)
- Speaking pace analysis
- Silence duration tracking
- Audio energy calculation

#### **7. observation_logger.py**
- Timestamped observation storage
- Behavioral pattern tracking
- Report generation with statistics

### **Frontend Components**

#### **1. app.js**
- WebSocket client management
- Interview state machine
- Text-to-Speech (TTS) integration
- Speech-to-Text (STT) microphone handling
- Message rendering and UI updates
- Camera streaming to backend

#### **2. avatar.js**
- **Three.js scene setup**: Camera, lighting, renderer
- **Avatar loading**: GLTF model from Ready Player Me
- **Morph target animation**: Visemes for lip-sync
- **Expression states**: 9+ facial expressions
- **Animation loop**: Smooth transitions and idle animations
- **Multi-avatar support**: Independent avatar instances

#### **3. observation_client.js**
- Polls `/observation/latest` endpoint
- Displays behavioral warnings
- Real-time metrics visualization
- Violation detection and alert display

#### **4. interview-state.js**
- State management for interview flow
- Subject/company selection handling
- Continuous mode logic

#### **5. toast.js**
- Non-intrusive notification system
- Success, warning, error, info types
- Auto-dismiss with timing control

#### **6. styles.css**
- Modern, professional styling
- Responsive layout
- Avatar canvas styling
- Animation keyframes for UI effects

---

## 🔄 System Workflow

### **Interview Session Flow**

```
1. USER OPENS APPLICATION
   ↓
2. CONSENT MODAL
   → User accepts privacy policy for camera/mic
   ↓
3. CAMERA/MIC PERMISSION
   → Browser requests permissions
   ↓
4. WEBSOCKET CONNECTION
   → Frontend connects to ws://localhost:8000/ws
   ↓
5. GREETING PHASE
   → Avatar greets candidate
   → Display: "When you're ready, click Start"
   ↓
6. START INTERVIEW
   → User clicks "Start Interview"
   → Observation engine starts (camera/audio monitoring)
   ↓
7. INTERVIEW STAGES
   ├─ WARM_UP: "Tell me about yourself"
   ├─ TECHNICAL: Subject-specific questions
   ├─ PROBLEM_SOLVING: Coding/design challenges
   ├─ BEHAVIORAL: "Describe a time when..."
   └─ STRESS: Pressure testing, follow-ups
   ↓
8. REAL-TIME MONITORING
   ├─ Face detection (multiple person check)
   ├─ Eye contact tracking
   ├─ Emotion analysis
   ├─ Voice stress detection
   └─ Behavioral warnings displayed
   ↓
9. CLOSURE PHASE
   → Avatar thanks candidate
   → "We'll be in touch soon"
   ↓
10. REPORT GENERATION
    → Final behavioral analysis report
    → Performance metrics
    ↓
11. END INTERVIEW
    → User clicks "End Interview"
    → Observation engine stops
    → WebSocket closes
```

### **AI Response Generation**

```
1. USER SENDS MESSAGE
   ↓
2. WEBSOCKET RECEIVES
   → payload: {text: "user answer"}
   ↓
3. INTERVIEW ENGINE PROCESSES
   → Builds conversation history
   → Constructs prompt with system instructions
   ↓
4. MODEL ROTATION
   → Check gemini-2.5-flash quota
   → If exhausted, try gemini-2.5-flash-lite
   → If exhausted, try gemini-2.5-pro
   ↓
5. API CALL TO GEMINI
   → Send prompt to selected model
   → Temperature: 0.55 (balanced creativity)
   ↓
6. FALLBACK CASCADE (if Gemini fails)
   ├─ Try Groq
   ├─ Try OpenRouter
   ├─ Try Hugging Face
   └─ Try Cohere
   ↓
7. PARSE JSON RESPONSE
   → Extract: system_state, interviewer_response,
              avatar_state, tts_enabled, etc.
   ↓
8. SEND TO FRONTEND
   → WebSocket sends JSON
   ↓
9. FRONTEND RENDERS
   → Update avatar expression
   → Display interviewer message
   → Trigger Text-to-Speech
```

---

## 📦 Installation & Setup

### **Prerequisites**
- **Python**: 3.10 or higher
- **Modern Browser**: Chrome, Edge, Safari (with Web Speech API)
- **Google Gemini API Key**: Free tier at [https://ai.google.dev](https://ai.google.dev)
- **Webcam & Microphone**: For behavioral observation

### **Backend Setup**

```bash
# Navigate to project directory
cd ai-interviewer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### **Environment Configuration**

Create `.env` file in project root:

```env
# Primary AI Model
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash

# Optional Fallback Providers
GROQ_API_KEY=your-groq-key
OPENROUTER_API_KEY=your-openrouter-key
HUGGINGFACE_API_KEY=your-huggingface-key
COHERE_API_KEY=your-cohere-key
```

### **Start Backend Server**

```bash
# From project root
python -m uvicorn backend.main:app --reload --port 8000

# OR from backend directory
cd backend
uvicorn main:app --reload --port 8000
```

Server runs at: `http://localhost:8000`

### **Frontend Setup**

```bash
# Navigate to frontend directory
cd frontend

# Start simple HTTP server
python -m http.server 5500

# OR use Node.js
npx http-server -p 5500

# OR use Live Server extension in VS Code
```

Open browser: `http://localhost:5500`

---

## 🌐 Browser Compatibility

| Feature | Chrome | Edge | Safari | Firefox |
|---------|:------:|:----:|:------:|:-------:|
| **3D Avatar (Three.js)** | ✅ | ✅ | ✅ | ✅ |
| **WebSocket** | ✅ | ✅ | ✅ | ✅ |
| **Text-to-Speech** | ✅ | ✅ | ✅ | ⚠️ Limited |
| **Speech-to-Text** | ✅ | ✅ | ✅ | ❌ |
| **WebRTC (Camera)** | ✅ | ✅ | ✅ | ✅ |
| **WebRTC (Microphone)** | ✅ | ✅ | ✅ | ✅ |

**Recommended Browsers**: Google Chrome or Microsoft Edge for full feature support.

---

## 🔮 Future Enhancements

### **Planned Features**
1. **Video Recording & Playback**
   - Record entire interview session
   - Playback with timestamp navigation
   - Video analysis for body language

2. **Advanced Analytics Dashboard**
   - Performance scoring with percentiles
   - Comparison with industry benchmarks
   - Detailed behavioral heatmaps
   - Progress tracking over multiple sessions

3. **Multi-language Support**
   - Interview in multiple languages
   - Automatic translation
   - Language proficiency assessment

4. **Custom Avatar Creation**
   - ReadyPlayerMe integration for custom avatars
   - Avatar personality customization
   - Different interviewer personas

5. **Interview History & Persistence**
   - Database integration (PostgreSQL/MongoDB)
   - Session history storage
   - Resume incomplete interviews

6. **Advanced Proctoring**
   - Browser tab switching detection
   - Screen sharing for code submissions
   - Background noise detection
   - Head pose angle limits

7. **Collaborative Features**
   - Real HR/interviewer takeover option
   - Multi-panel interviews with 3+ avatars
   - Peer interview practice mode

8. **Mobile Application**
   - iOS and Android apps
   - Mobile-optimized 3D avatars
   - Touch-based interactions

9. **Integration APIs**
   - ATS (Applicant Tracking System) integration
   - LinkedIn profile import
   - Resume parsing for personalized questions

10. **AI Model Improvements**
    - Fine-tuned models for specific domains
    - Custom company-specific question banks
    - Adaptive difficulty based on performance

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🤝 Contributing

For contribution guidelines, bug reports, or feature requests, please contact the development team.

---

## 📧 Support

For technical support or questions:
- Email: support@ai-interviewer.com
- Documentation: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- Quick Start: [QUICK_START.md](QUICK_START.md)

---

**Last Updated**: January 7, 2026  
**Version**: 1.0.0  
**Maintained By**: AI Interviewer Development Team
