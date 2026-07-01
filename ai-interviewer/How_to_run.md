# 🚀 How to Run HireSense AI

This guide provides step-by-step instructions for running HireSense AI with both synthetic and real datasets.

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Creating Synthetic Dataset](#creating-synthetic-dataset)
3. [Running with Synthetic Data](#running-with-synthetic-data)
4. [Running with Real Data](#running-with-real-data)
5. [Evaluating and Scoring](#evaluating-and-scoring)
6. [Viewing Results](#viewing-results)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Initial Setup

### Step 1: Install Dependencies

**Option A: Automated Setup (Recommended)**

**Windows:**
```powershell
# Run from project root directory
.\scripts\setup_models_windows.ps1
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x scripts/setup_models_linux.sh

# Run setup
./scripts/setup_models_linux.sh
```

This script will:
- ✅ Install all Python dependencies
- ✅ Download YOLOv8 model (yolov8s.pt)
- ✅ Install MediaPipe, DeepFace, OpenCV
- ✅ Generate synthetic dataset (100 sessions)

**Option B: Manual Setup**

```bash
# Install Python packages
pip install -r backend/requirements.txt

# Download YOLOv8 model
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# Move model to backend folder
# Windows PowerShell:
Move-Item yolov8s.pt backend/yolov8s.pt

# Linux/Mac:
mv yolov8s.pt backend/yolov8s.pt
```

### Step 2: Verify Installation

```bash
# Check if YOLOv8 model exists
ls backend/yolov8s.pt

# Verify Python packages
pip list | grep -E "mediapipe|ultralytics|deepface|opencv-python|fastapi"
```

---

## 📊 Creating Synthetic Dataset

### What is Synthetic Data?

Synthetic data is **artificially generated interview sessions** that simulate real candidates. This is useful for:
- Testing the system without real interviews
- Training and validation
- Research and development
- Demonstrating the platform

### Generate Synthetic Dataset

**Method 1: Default Generation (100 sessions)**

```bash
python backend/synthetic_data_generator.py
```

**Method 2: Custom Number of Sessions**

```bash
# Generate 50 sessions
python backend/synthetic_data_generator.py --num-sessions 50

# Generate 200 sessions
python backend/synthetic_data_generator.py --num-sessions 200
```

**Method 3: Custom Output Directory**

```bash
python backend/synthetic_data_generator.py --num-sessions 100 --output-dir custom_dataset/synthetic
```

### What Gets Generated?

After running the generator, you'll see:

```
dataset/
└── synthetic/
    ├── index.json                    # Summary of all sessions
    ├── session_<uuid_1>/
    │   ├── video_metadata.json       # Session metadata
    │   ├── transcript.json            # Interview Q&A
    │   ├── gaze_metrics.json          # Eye tracking data
    │   ├── emotion_metrics.json       # Emotion timeline
    │   ├── proctoring_metrics.json    # Violations
    │   └── final_report.json          # Scores and decision
    ├── session_<uuid_2>/
    │   └── [same structure]
    └── ... (100 sessions total)
```

### Verify Synthetic Data Creation

```bash
# Check number of sessions created
# Windows PowerShell:
(Get-ChildItem dataset/synthetic/session_* -Directory).Count

# Linux/Mac:
ls -d dataset/synthetic/session_* | wc -l

# View index file
cat dataset/synthetic/index.json
```

**Expected Output:**
```json
{
  "generated_at": "2026-02-14T10:30:00",
  "total_sessions": 100,
  "sessions": [
    {
      "session_id": "abc123...",
      "quality": "Hire",
      "overall_score": 78.5
    },
    ...
  ]
}
```

---

## 🎮 Running with Synthetic Data

Synthetic mode uses pre-generated data without requiring real camera/microphone.

### Step 1: Configure Synthetic Mode

Edit `config.json`:

```json
{
  "DATA_MODE": "synthetic",
  "DATASET_PATH": "dataset",
  "PROCTORING": {
    "multi_person_threshold_seconds": 3,
    "look_away_threshold_seconds": 10,
    "warning_limit": 3,
    "enable_violations": true
  }
}
```

**Key Setting:** `"DATA_MODE": "synthetic"`

### Step 2: Start Backend

```bash
# Navigate to backend directory
cd backend

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
[INFO] Configuration loaded: DATA_MODE=synthetic
[INFO] Human Observation Engine initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Access Synthetic Reports

**Option A: Via API**

```bash
# Get list of all sessions from index
curl http://localhost:8000/observation/report

# Get specific session report
curl http://localhost:8000/report/abc123-session-id
```

**Option B: Directly Read Files**

```bash
# View a specific session report
cat dataset/synthetic/session_abc123/final_report.json

# View all session scores
python -c "
import json
from pathlib import Path

for session_dir in Path('dataset/synthetic').glob('session_*/'):
    report = json.load(open(session_dir / 'final_report.json'))
    print(f\"{report['session_id'][:8]}: {report['hire_decision']} ({report['scores']['overall_score']:.1f}/100)\")
"
```

### Step 4: Evaluate Synthetic Dataset

See [Evaluating and Scoring](#evaluating-and-scoring) section below.

---

## 🎥 Running with Real Data

Real mode captures live interview sessions with actual camera and microphone.

### Step 1: Configure Real Mode

Edit `config.json`:

```json
{
  "DATA_MODE": "real",
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
  },
  "LOGGING": {
    "save_video_metadata": true,
    "save_transcripts": true,
    "save_metrics": true,
    "generate_reports": true
  }
}
```

**Key Setting:** `"DATA_MODE": "real"`

### Step 2: Start Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Frontend

**Option A: Using Python HTTP Server**

```bash
# Open new terminal
cd frontend
python -m http.server 8080
```

Then open browser: `http://localhost:8080`

**Option B: Direct File Access**

Simply open `frontend/index.html` in your browser (Chrome recommended).

### Step 4: Conduct Real Interview

1. **Grant Permissions**
   - Browser will ask for camera/microphone access
   - Click "Allow" for both

2. **Configure Interview**
   - Select **Subject** (e.g., "Python", "System Design")
   - Select **Company** (e.g., "Google", "Startup")
   - Select **Mode** (Individual or Multi Interviewer)

3. **Start Interview**
   - Click **"Start Interview"** button
   - Accept consent modal
   - Wait for AI greeting

4. **Answer Questions**
   - **Type answers** in text field, or
   - **Speak answers** by clicking 🎤 microphone button

5. **Monitor Proctoring Dashboard**
   - Watch real-time metrics in top-right panel:
     - Eye Contact %
     - Gaze Direction
     - Head Pose
     - Blink Rate
     - Emotion
     - Stress Level
     - Person Count
     - Warnings

6. **Complete Interview**
   - Answer all interview stages: WARM_UP → TECHNICAL → BEHAVIORAL → STRESS
   - Click **"End Interview"** when done

### Step 5: Access Real Session Data

After interview completion, data is saved to:

```
dataset/
└── sessions/
    └── session_<uuid>/
        ├── video_metadata.json
        ├── transcript.json
        ├── gaze_metrics.json
        ├── emotion_metrics.json
        ├── proctoring_metrics.json
        └── final_report.json
```

**View the report:**

```bash
# Find latest session
ls -lt dataset/sessions/

# View report
cat dataset/sessions/session_<your_uuid>/final_report.json
```

---

## 📈 Evaluating and Scoring

### Automatic Scoring

HireSense AI includes an automated scoring system that evaluates interviews based on:
- Technical competency
- Communication skills
- Clarity and structure
- Confidence
- Proctoring compliance

### Score a Single Session

```bash
python backend/auto_score_generator.py --session-dir dataset/sessions/session_abc123
```

**Output:**
```
✅ Session scored: Hire (78.5/100)
```

This creates/updates `final_report.json` with comprehensive scores.

### Score Entire Synthetic Dataset

```bash
python backend/auto_score_generator.py --dataset-dir dataset/synthetic
```

**Output:**
```
📊 Scoring 100 sessions...
  Scored 10/100 sessions...
  Scored 20/100 sessions...
  ...
  Scored 100/100 sessions...

✅ Scoring complete!
📈 Results:
   - Hire: 38
   - Maybe: 32
   - Reject: 30
   - Average score: 58.42/100
```

### Score All Real Sessions

```bash
python backend/auto_score_generator.py --dataset-dir dataset/sessions
```

### Understanding the Scoring

**Generated `final_report.json` contains:**

```json
{
  "session_id": "abc123",
  "candidate_name": "Candidate_001",
  "position": "Software Engineer",
  "scores": {
    "technical_score": 8.2,         // 0-10 scale
    "communication_score": 7.5,      // 0-10 scale
    "clarity_score": 8.0,            // 0-10 scale
    "confidence_score": 7.8,         // 0-10 scale
    "overall_score": 78.5,           // 0-100 scale
    "overall_score_before_penalties": 82.0
  },
  "behavioral_analysis": {
    "eye_contact_percentage": 78.5,
    "dominant_emotion": "confident",
    "stress_level": "low",
    "engagement_score": 0.85
  },
  "proctoring_summary": {
    "total_violations": 2,
    "violation_types": ["EXCESSIVE_LOOK_AWAY"],
    "total_penalty_points": 3.5,
    "suspicious_activity_score": 0.15
  },
  "hire_decision": "Hire",           // Hire / Maybe / Reject
  "recommendation": "Strong candidate with excellent overall performance..."
}
```

**Scoring Algorithm:**

1. **Base Scores** (0-10 each):
   - Technical: Answer depth, keywords, technical accuracy
   - Communication: Eye contact, emotion, filler words
   - Clarity: Answer structure, length, organization
   - Confidence: Gaze stability, response time, emotion

2. **Overall Score** (0-100):
   ```
   Overall = (Technical × 0.4 + Communication × 0.25 + 
              Clarity × 0.2 + Confidence × 0.15) × 10
   ```

3. **Apply Penalties**:
   - Multiple persons: -20 points
   - Phone detected: -15 points
   - Excessive look-away: -10 points
   - Face not detected: -5 points

4. **Hire Decision**:
   - **Hire**: Score ≥ 70 AND no critical violations
   - **Maybe**: Score ≥ 50
   - **Reject**: Score < 50 OR critical violations

---

## 📊 Viewing Results

### View Individual Session

**Method 1: Pretty Print JSON**

```bash
# Windows PowerShell:
python -m json.tool dataset/synthetic/session_abc123/final_report.json

# Linux/Mac:
cat dataset/synthetic/session_abc123/final_report.json | python -m json.tool
```

**Method 2: View Specific Metrics**

```python
import json

# Load report
with open('dataset/synthetic/session_abc123/final_report.json') as f:
    report = json.load(f)

# Print summary
print(f"Candidate: {report['candidate_name']}")
print(f"Position: {report['position']}")
print(f"Overall Score: {report['scores']['overall_score']}/100")
print(f"Decision: {report['hire_decision']}")
print(f"\nRecommendation:\n{report['recommendation']}")
```

### Analyze Dataset Statistics

**Create Summary Report:**

```python
import json
from pathlib import Path
from collections import defaultdict

def analyze_dataset(dataset_dir):
    """Analyze entire dataset and print statistics."""
    
    sessions = []
    decisions = defaultdict(int)
    scores = []
    
    # Load all sessions
    for session_dir in Path(dataset_dir).glob('session_*/'):
        report_file = session_dir / 'final_report.json'
        if report_file.exists():
            with open(report_file) as f:
                report = json.load(f)
                sessions.append(report)
                decisions[report['hire_decision']] += 1
                scores.append(report['scores']['overall_score'])
    
    # Print statistics
    print(f"\n{'='*60}")
    print(f"DATASET ANALYSIS: {dataset_dir}")
    print(f"{'='*60}\n")
    
    print(f"Total Sessions: {len(sessions)}")
    print(f"\nHire Decisions:")
    for decision, count in sorted(decisions.items()):
        percentage = (count / len(sessions)) * 100
        print(f"  {decision}: {count} ({percentage:.1f}%)")
    
    print(f"\nScore Statistics:")
    print(f"  Average: {sum(scores) / len(scores):.2f}")
    print(f"  Minimum: {min(scores):.2f}")
    print(f"  Maximum: {max(scores):.2f}")
    print(f"  Median: {sorted(scores)[len(scores)//2]:.2f}")
    
    # Violation analysis
    total_violations = sum(
        report['proctoring_summary']['total_violations'] 
        for report in sessions
    )
    print(f"\nProctoring Violations:")
    print(f"  Total: {total_violations}")
    print(f"  Average per session: {total_violations / len(sessions):.2f}")
    
    print(f"\n{'='*60}\n")

# Run analysis
analyze_dataset('dataset/synthetic')
```

**Save and run:**

```bash
python analyze_dataset.py
```

**Expected Output:**

```
============================================================
DATASET ANALYSIS: dataset/synthetic
============================================================

Total Sessions: 100

Hire Decisions:
  Hire: 38 (38.0%)
  Maybe: 32 (32.0%)
  Reject: 30 (30.0%)

Score Statistics:
  Average: 58.42
  Minimum: 22.50
  Maximum: 92.30
  Median: 59.15

Proctoring Violations:
  Total: 45
  Average per session: 0.45

============================================================
```

### Export to CSV for Excel Analysis

```python
import json
import csv
from pathlib import Path

def export_to_csv(dataset_dir, output_file='results.csv'):
    """Export dataset to CSV for analysis."""
    
    sessions = []
    for session_dir in Path(dataset_dir).glob('session_*/'):
        report_file = session_dir / 'final_report.json'
        if report_file.exists():
            with open(report_file) as f:
                sessions.append(json.load(f))
    
    # Write CSV
    with open(output_file, 'w', newline='') as f:
        fieldnames = [
            'session_id', 'candidate_name', 'position',
            'technical_score', 'communication_score', 'clarity_score', 'confidence_score',
            'overall_score', 'eye_contact_percentage', 'dominant_emotion', 'stress_level',
            'total_violations', 'hire_decision'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for session in sessions:
            writer.writerow({
                'session_id': session['session_id'],
                'candidate_name': session['candidate_name'],
                'position': session['position'],
                'technical_score': session['scores']['technical_score'],
                'communication_score': session['scores']['communication_score'],
                'clarity_score': session['scores']['clarity_score'],
                'confidence_score': session['scores']['confidence_score'],
                'overall_score': session['scores']['overall_score'],
                'eye_contact_percentage': session['behavioral_analysis']['eye_contact_percentage'],
                'dominant_emotion': session['behavioral_analysis']['dominant_emotion'],
                'stress_level': session['behavioral_analysis']['stress_level'],
                'total_violations': session['proctoring_summary']['total_violations'],
                'hire_decision': session['hire_decision']
            })
    
    print(f"✅ Exported {len(sessions)} sessions to {output_file}")

# Export synthetic dataset
export_to_csv('dataset/synthetic')

# Export real sessions
export_to_csv('dataset/sessions', 'real_results.csv')
```

---

## 🐛 Troubleshooting

### Issue: Synthetic data generation fails

**Error:** `ModuleNotFoundError: No module named 'ultralytics'`

**Solution:**
```bash
pip install ultralytics numpy
```

---

### Issue: Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r backend/requirements.txt
```

---

### Issue: YOLOv8 model not found

**Error:** `FileNotFoundError: yolov8s.pt not found`

**Solution:**
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
# Move to backend directory
Move-Item yolov8s.pt backend/yolov8s.pt  # Windows
# or
mv yolov8s.pt backend/yolov8s.pt  # Linux/Mac
```

---

### Issue: Camera not working in real mode

**Possible Causes:**
1. Browser doesn't have camera permissions
2. Another application is using the camera
3. Browser doesn't support WebRTC

**Solution:**
1. Grant camera permissions in browser
2. Close other apps using camera (Zoom, Skype, etc.)
3. Use Chrome or Edge (recommended browsers)

---

### Issue: No data being saved in real mode

**Check:**
1. Verify `config.json` has `"DATA_MODE": "real"`
2. Check backend logs for errors
3. Ensure `LOGGING` settings are enabled in config

**Solution:**
```bash
# Restart backend with logging
cd backend
uvicorn main:app --reload --log-level debug
```

---

### Issue: Scoring script returns empty results

**Error:** `No sessions found in <directory>`

**Solution:**
```bash
# Verify sessions exist
ls dataset/synthetic/session_*

# Check file structure
ls dataset/synthetic/session_abc123/
# Should contain: final_report.json, gaze_metrics.json, etc.

# Regenerate if needed
python backend/synthetic_data_generator.py --num-sessions 100
```

---

## 📚 Quick Reference Commands

### Setup
```bash
# Windows
.\scripts\setup_models_windows.ps1

# Linux/Mac
./scripts\setup_models_linux.sh
```

### Generate Synthetic Data
```bash
python backend/synthetic_data_generator.py --num-sessions 100
```

### Start Application
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && python -m http.server 8080
```

### Score Sessions
```bash
# Score all synthetic sessions
python backend/auto_score_generator.py --dataset-dir dataset/synthetic

# Score all real sessions
python backend/auto_score_generator.py --dataset-dir dataset/sessions

# Score single session
python backend/auto_score_generator.py --session-dir dataset/sessions/session_abc123
```

### Switch Modes
```bash
# Edit config.json
"DATA_MODE": "synthetic"  # For testing with synthetic data
"DATA_MODE": "real"       # For live interviews
```

---

## ✅ Verification Checklist

Before running evaluations, ensure:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] YOLOv8 model exists at `backend/yolov8s.pt`
- [ ] Synthetic dataset generated (100+ sessions)
- [ ] `config.json` configured correctly
- [ ] Backend starts without errors
- [ ] Frontend accessible in browser

---

## 🎓 Best Practices

1. **Always generate synthetic data first** before testing real interviews
2. **Run scoring on synthetic data** to verify the system works
3. **Use synthetic mode** for development and testing
4. **Switch to real mode** only for production interviews
5. **Backup dataset folders** before making changes
6. **Export to CSV** for detailed statistical analysis
7. **Review final_report.json** for comprehensive insights

---

## 📞 Support

For issues or questions:
- Check [README.md](README.md) for detailed documentation
- Review backend logs: `uvicorn main:app --log-level debug`
- Verify `config.json` settings
- Ensure all dependencies are installed

---

**Happy Interviewing! 🚀**
