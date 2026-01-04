"""
Observation Engine Configuration
Centralized settings for all observation analyzers.
"""

# ============================================================================
# CAMERA SETTINGS
# ============================================================================

# Camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Camera FPS (lower = less CPU usage)
CAMERA_FPS = 15

# ============================================================================
# FACE ANALYZER SETTINGS
# ============================================================================

# Eye detection threshold (lower = easier to detect closed eyes)
EYE_ASPECT_RATIO_THRESHOLD = 0.2

# Head direction thresholds (degrees)
YAW_LOOKING_AWAY_THRESHOLD = 25  # Head turn left/right
PITCH_LOOKING_AWAY_THRESHOLD = 20  # Head turn up/down

# ============================================================================
# EMOTION ANALYZER SETTINGS
# ============================================================================

# Emotion model type: 'heuristic' or 'model'
EMOTION_MODEL_TYPE = 'heuristic'

# Optional path to local emotion model
EMOTION_MODEL_PATH = None  # e.g., './emotion_model.onnx'

# ============================================================================
# AUDIO ANALYZER SETTINGS
# ============================================================================

# Audio sample rate (Hz)
AUDIO_SAMPLE_RATE = 16000

# Audio chunk size (samples)
AUDIO_CHUNK_SIZE = 2048

# Expected pitch range (Hz)
MIN_PITCH = 80
MAX_PITCH = 400

# Stress detection thresholds
PITCH_DEVIATION_HIGH_STRESS = 0.3  # 30% deviation = high stress
PITCH_DEVIATION_MEDIUM_STRESS = 0.15  # 15% = medium stress
ENERGY_DEVIATION_HIGH_STRESS = 0.4  # 40% deviation = high stress
ENERGY_DEVIATION_MEDIUM_STRESS = 0.2  # 20% = medium stress

# ============================================================================
# PACE CONTROLLER SETTINGS
# ============================================================================

# Stress threshold (0-1)
STRESS_THRESHOLD = 0.6

# Looking away threshold (seconds)
LOOKING_AWAY_THRESHOLD = 5

# Silence threshold (seconds)
SILENCE_THRESHOLD = 3

# Pace adjustments
STRESS_DELAY = 2  # seconds to delay next question
LOOKING_AWAY_DELAY = 1  # seconds to delay next question
SILENCE_DELAY = 1  # seconds to delay next question

# ============================================================================
# OBSERVATION ENGINE SETTINGS
# ============================================================================

# Observation loop frequency (seconds)
OBSERVATION_LOOP_INTERVAL = 0.1  # ~10 Hz

# Frontend polling frequency (milliseconds)
FRONTEND_POLLING_INTERVAL = 500  # 500ms

# Maximum queue sizes
FRAME_QUEUE_SIZE = 5
AUDIO_QUEUE_SIZE = 10
OBSERVATION_QUEUE_SIZE = 100

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log detailed observations
DETAILED_LOGGING = False

# Enable debug output
DEBUG_MODE = True

# ============================================================================
# REPORT GENERATION SETTINGS
# ============================================================================

# Score ranges
EYE_CONTACT_PERFECT = 8  # Excellent eye contact
EYE_CONTACT_GOOD = 6     # Good eye contact
EYE_CONTACT_FAIR = 4     # Fair eye contact

VOICE_CONFIDENCE_EXCELLENT = 8
VOICE_CONFIDENCE_GOOD = 6
VOICE_CONFIDENCE_FAIR = 4

# Stress level mapping
STRESS_HIGH_RATIO = 0.3  # > 30% of time in high stress
STRESS_MEDIUM_RATIO = 0.5  # > 50% of time in medium/high stress

# ============================================================================
# VIOLATION THRESHOLDS
# ============================================================================

# Number of looking away incidents before flagging
LOOKING_AWAY_INCIDENT_THRESHOLD = 5

# Number of high stress incidents before flagging
HIGH_STRESS_INCIDENT_THRESHOLD = 3

# Number of long silence incidents before flagging
LONG_SILENCE_INCIDENT_THRESHOLD = 1

# Number of face not detected incidents before flagging
FACE_NOT_DETECTED_INCIDENT_THRESHOLD = 2
