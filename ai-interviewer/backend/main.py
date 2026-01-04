import asyncio
import json
import pathlib
import sys
from typing import Any, Dict, List
import numpy as np
import base64
import cv2

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState


def sanitize_for_json(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# Allow running both as package (recommended) and as script from backend/ directory.
try:
    from .interview_engine import InterviewEngine, MockInterviewEngine
    from .human_observation_engine import HumanObservationEngine
except ImportError:  # pragma: no cover - fallback for direct execution
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
    from backend.interview_engine import InterviewEngine, MockInterviewEngine
    from backend.human_observation_engine import HumanObservationEngine

app = FastAPI(title="AI Interviewer", version="1.0.0")

# Add CORS middleware FIRST before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

print("[INFO] CORS middleware configured for all origins")

SYSTEM_PROMPT_PATH = pathlib.Path(__file__).parent / "system_prompt.txt"
ENV_PATH = pathlib.Path(__file__).resolve().parents[1] / ".env"

# Load environment variables from project-level .env if present.
load_dotenv(ENV_PATH)

# Initialize observation engine (global instance)
try:
    observation_engine = HumanObservationEngine()
    print("[INFO] Human Observation Engine initialized successfully")
except Exception as e:
    print(f"[WARNING] Failed to initialize observation engine: {e}")
    print("[INFO] Interview will continue without behavioral observation")
    observation_engine = None


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def get_engine() -> InterviewEngine:
    prompt = load_system_prompt()
    # Fallback to mock engine when API key is absent to keep local dev usable.
    try:
        return InterviewEngine(system_prompt=prompt)
    except RuntimeError as exc:
        if "OPENAI_API_KEY" in str(exc):
            return MockInterviewEngine()
        raise


def get_mock_engine() -> InterviewEngine:
    return MockInterviewEngine()


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, engine: InterviewEngine = Depends(get_engine)
) -> None:
    await websocket.accept()
    history: List[Dict[str, str]] = []
    interview_started = False
    violation_detected = False
    
    try:
        # Start observation engine
        if observation_engine is not None:
            observation_engine.start()
        
        # Send greeting message immediately upon connection
        greeting_response = await engine.run_turn(user_text="", history=history)
        history.append({"role": "assistant", "content": greeting_response.get("interviewer_response", "")})
        await websocket.send_json(greeting_response)
        
        while True:
            # Check for proctoring violations
            if observation_engine is not None:
                latest_obs = observation_engine.get_latest_observation()
                if latest_obs:
                    face_data = latest_obs.get("face", {})
                    if face_data.get("multiple_faces") or face_data.get("violation"):
                        violation_detected = True
                        await websocket.send_json({
                            "system_state": "TERMINATED",
                            "interviewer_response": "Interview terminated: Multiple persons detected. This is a proctoring violation.",
                            "avatar_state": "neutral_disappointed",
                            "tts_enabled": True,
                            "ui_mode": "violation",
                            "next_action": "terminate",
                            "violation_type": "MULTIPLE_PERSONS"
                        })
                        break
            
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "error": "Invalid payload",
                        "system_state": "ERROR",
                        "avatar_state": "neutral_disappointed",
                    }
                )
                continue

            user_text = payload.get("text") or ""
            if not user_text.strip():
                continue
                
            history.append({"role": "user", "content": user_text})

            ai_response = await engine.run_turn(user_text=user_text, history=history)
            history.append({"role": "assistant", "content": ai_response.get("interviewer_response", "")})

            await websocket.send_json(ai_response)
    except WebSocketDisconnect:
        if observation_engine is not None:
            observation_engine.stop()
        return
    except Exception as exc:  # safeguard
        if observation_engine is not None:
            observation_engine.stop()
        if websocket.application_state != WebSocketState.CONNECTED:
            return
        await websocket.send_json(
            {
                "system_state": "ERROR",
                "interviewer_response": "The interview encountered an issue. Please reconnect.",
                "avatar_state": "neutral_disappointed",
                "tts_enabled": False,
                "ui_mode": "professional_minimal",
                "next_action": "terminate",
                "details": str(exc),
            }
        )


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


# ============================================================================
# Human Observation & Behavior Analysis Endpoints
# ============================================================================

@app.post("/observation/start")
async def start_observation() -> Dict[str, Any]:
    """Start the observation engine (camera + audio monitoring)."""
    if observation_engine is None:
        return {"success": True, "message": "Observation not available, interview proceeding without behavioral analysis"}
    success = observation_engine.start()
    return {
        "success": success,
        "message": "Observation engine started" if success else "Failed to start observation engine"
    }


@app.post("/observation/stop")
async def stop_observation() -> Dict[str, str]:
    """Stop the observation engine."""
    if observation_engine is not None:
        observation_engine.stop()
    return {"success": "true", "message": "Observation engine stopped"}


@app.post("/observation/add_audio")
async def add_audio_frame(payload: Dict[str, Any]) -> Dict[str, str]:
    """Add audio frame for analysis (base64 encoded)."""
    if observation_engine is None:
        return {"success": "true"}
    import base64
    try:
        audio_base64 = payload.get("audio_data", "")
        if audio_base64:
            audio_bytes = base64.b64decode(audio_base64)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            observation_engine.add_audio_frame(audio_array)
        return {"success": "true"}
    except Exception as e:
        return {"success": "false", "error": str(e)}


@app.post("/observation/add_video_frame")
async def add_video_frame(payload: Dict[str, Any]) -> Dict[str, str]:
    """Add video frame for analysis (base64 encoded image)."""
    if observation_engine is None:
        return {"success": "true"}
    import base64
    import cv2
    try:
        frame_base64 = payload.get("frame_data", "")
        if frame_base64:
            # Decode base64 to image
            img_bytes = base64.b64decode(frame_base64)
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if frame is not None:
                observation_engine.add_video_frame(frame)
                return {"success": "true"}
        return {"success": "false", "error": "No frame data"}
    except Exception as e:
        return {"success": "false", "error": str(e)}


@app.options("/observation/latest")
async def options_latest():
    """Handle CORS preflight for /observation/latest"""
    return {"status": "ok"}


@app.get("/observation/latest")
async def get_latest_observation() -> Dict[str, Any]:
    """Get the latest behavioral observation."""
    if observation_engine is None:
        return {"success": True, "observation": None, "warnings": []}
    
    obs = observation_engine.get_latest_observation()
    warnings = []
    
    if obs:
        # Check for violations
        face_data = obs.get("face", {})
        
        # Multiple persons detected (YOLOv8 based - much more reliable)
        if face_data.get("multiple_faces") or face_data.get("face_count", 0) > 1:
            warnings.append({
                "type": "VIOLATION",
                "severity": "CRITICAL",
                "message": "⚠️ Multiple persons detected in frame! Please ensure only you are visible to the camera.",
                "icon": "🚨"
            })
        
        # Eye contact detection with proper confidence-based thresholds
        # These thresholds are based on actual camera looking values:
        # 0.8-1.0 = looking at camera (good)
        # 0.5-0.8 = mostly looking (acceptable)
        # 0.3-0.5 = borderline (warning)
        # 0.0-0.3 = not looking (warning)
        eye_contact = face_data.get("eye_contact_confidence", 0.5)
        looking_away = face_data.get("looking_away", False)
        
        # Only warn if eye contact is low (< 0.35) AND explicitly looking away
        # This prevents false positives from slight head movements
        if eye_contact < 0.35 and looking_away:
            warnings.append({
                "type": "BEHAVIOR",
                "severity": "WARNING",
                "message": "👁️ You're looking away from the camera. Please maintain eye contact with the camera lens.",
                "icon": "⚠️"
            })
        # Additional warning for very low eye contact (< 0.25) regardless of looking_away
        elif eye_contact < 0.25:
            warnings.append({
                "type": "BEHAVIOR",
                "severity": "WARNING",
                "message": "👁️ Please look at the camera. Eye contact is important for the interview.",
                "icon": "⚠️"
            })
        
        # Face not detected
        if not face_data.get("face_detected", False):
            warnings.append({
                "type": "TECHNICAL",
                "severity": "WARNING",
                "message": "📸 Face not detected. Please ensure you're visible in the camera frame.",
                "icon": "⚠️"
            })
        
        # Sanitize observation data
        sanitized_obs = sanitize_for_json({
            "timestamp": obs.get("timestamp", 0),
            "face": obs.get("face", {}),
            "emotion": obs.get("emotion", {}),
            "audio": obs.get("audio", {}),
            "pace_adjustment": obs.get("pace_adjustment", {}),
        })
        
        return {
            "success": True,
            "observation": sanitized_obs,
            "warnings": warnings
        }
    
    return {"success": True, "observation": None, "warnings": []}


@app.get("/observation/report")
async def get_observation_report() -> Dict[str, Any]:
    """Get final behavioral analysis report."""
    if observation_engine is None:
        return {"success": True, "report": None}
    report = observation_engine.get_report()
    return {
        "success": True,
        "report": sanitize_for_json(report)
    }
    report = observation_engine.generate_report()
    return {"success": True, "report": report}


@app.post("/observation/reset")
async def reset_observation() -> Dict[str, str]:
    """Reset observation engine for new interview."""
    if observation_engine is not None:
        observation_engine.reset()
    return {"success": True, "message": "Observation engine reset"}

