import { initAvatar, setAvatarState, startMouth, stopMouth } from "./avatar.js";
import { ObservationClient } from "./observation_client.js";

const canvas = document.getElementById("avatar-canvas");
const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("input-form");
const inputEl = document.getElementById("text-input");
const startBtn = document.getElementById("start-btn");
const endBtn = document.getElementById("end-btn");
const continuousBtn = document.getElementById("continuous-btn");
const stageLabel = document.getElementById("stage-label");
const avatarStateLabel = document.getElementById("avatar-state");
const connectionLabel = document.getElementById("connection-label");
const speakBtn = document.getElementById("speak-btn");
const cameraPanel = document.getElementById("camera-panel");
const candidateVideo = document.getElementById("candidate-video");

// Observation client
const observation = new ObservationClient();
observation.setVideoElement(candidateVideo);

// Speaking indicator
const speakingIndicator = document.getElementById("speaking-indicator");
let audioAnalyzer = null;
let audioAnimationFrame = null;

// Consent modal
const consentModal = document.getElementById("consent-modal");
const consentAccept = document.getElementById("consent-accept");
const consentDecline = document.getElementById("consent-decline");
let consentGiven = false;

consentAccept.addEventListener("click", async () => {
  console.log("[DEBUG] Consent accepted, starting camera...");
  
  // Hide modal immediately
  consentModal.classList.add("hidden");
  consentGiven = true;
  
  try {
    // Start observation after consent
    const success = await observation.startObservation();
    if (success) {
      console.log("[DEBUG] Camera started successfully");
      
      // Start polling immediately to begin analysis
      observation.startPolling();
      console.log("[DEBUG] Started observation polling immediately");
      
      // Wait a bit for stream to be ready then start audio visualization
      setTimeout(() => {
        startAudioVisualization();
        console.log("[DEBUG] Audio visualization started");
      }, 800);
      
      // After camera is ready, proceed to connect WebSocket
      connect();
    } else {
      console.error("[DEBUG] Failed to start camera");
      alert("Failed to access camera/microphone. Please check permissions.");
      setStartButtonState("idle");
    }
  } catch (err) {
    console.error("[ERROR] Camera startup failed:", err);
    alert("Failed to access camera/microphone. Please check permissions.");
    setStartButtonState("idle");
  }
});

consentDecline.addEventListener("click", () => {
  alert("Interview requires camera and microphone consent.");
  consentModal.classList.add("hidden");
  setStartButtonState("idle");
});

let ws;
let connected = false;
let connecting = false;
let handshakeComplete = false;
let speechActive = false;
let interviewStarted = false;
let isListening = false;
let continuousMode = false;
let waitingForAI = false;
let connectTimeout;

function setStartButtonState(state) {
  if (state === "connecting") {
    startBtn.disabled = true;
    startBtn.textContent = "Connecting...";
  } else if (state === "connected") {
    startBtn.disabled = true;
    startBtn.textContent = "Connected";
  } else {
    startBtn.disabled = false;
    startBtn.textContent = "Start Interview";
  }
}

// Initialize speech recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let speechTimeout;
let accumulatedTranscript = "";

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = true; // Changed to true for better pause handling
  recognition.interimResults = true;
  recognition.lang = "en-US";
  
  recognition.onstart = () => {
    isListening = true;
    accumulatedTranscript = "";
    speakBtn.classList.add("listening");
    speakBtn.textContent = "⏹️";
    console.log("[DEBUG] Speech recognition started");
  };
  
  recognition.onresult = (event) => {
    let interimTranscript = "";
    let finalTranscript = "";
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }
    
    // Update accumulated transcript with final results
    if (finalTranscript) {
      accumulatedTranscript += finalTranscript + " ";
      console.log("[DEBUG] Accumulated transcript:", accumulatedTranscript.substring(0, 50));
    }
    
    // Show current text (accumulated + interim)
    inputEl.value = accumulatedTranscript + interimTranscript;
    
    // Clear any existing timeout
    if (speechTimeout) {
      clearTimeout(speechTimeout);
    }
    
    // Set 3-second timeout after last speech detected
    speechTimeout = setTimeout(() => {
      const finalText = accumulatedTranscript.trim();
      if (finalText && connected && !waitingForAI) {
        console.log("[DEBUG] 3-second pause detected, sending:", finalText);
        recognition.stop();
        sendUserMessage(finalText);
        accumulatedTranscript = "";
        inputEl.value = "";
      }
    }, 3000); // 3 seconds pause before sending
  };
  
  recognition.onend = () => {
    isListening = false;
    speakBtn.classList.remove("listening");
    speakBtn.textContent = "🎤";
    inputEl.placeholder = "Type your response";
    if (speechTimeout) {
      clearTimeout(speechTimeout);
      speechTimeout = null;
    }
    console.log("[DEBUG] Speech recognition ended");
  };
  
  recognition.onerror = (event) => {
    isListening = false;
    speakBtn.classList.remove("listening");
    speakBtn.textContent = "🎤";
    if (speechTimeout) {
      clearTimeout(speechTimeout);
      speechTimeout = null;
    }
    console.error("[ERROR] Speech recognition error:", event.error);
    if (event.error !== 'no-speech') {
      appendMessage("System", `Speech error: ${event.error}`);
    }
  };
} else {
  console.warn("[WARNING] Speech recognition not supported in this browser");
}

// Buzzer sound effect
function playBuzzer() {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch (e) {
    console.error("[ERROR] Buzzer sound failed:", e);
  }
}

speakBtn.addEventListener("click", (e) => {
  e.preventDefault();
  if (!recognition) {
    appendMessage("System", "Speech recognition not available in this browser");
    return;
  }
  if (isListening) {
    // Stop listening and send if we have text
    if (speechTimeout) {
      clearTimeout(speechTimeout);
      speechTimeout = null;
    }
    recognition.stop();
    const finalText = accumulatedTranscript.trim();
    if (finalText && connected && !waitingForAI) {
      sendUserMessage(finalText);
      accumulatedTranscript = "";
      inputEl.value = "";
    }
  } else {
    playBuzzer();
    inputEl.value = "";
    accumulatedTranscript = "";
    inputEl.placeholder = "🎙️ Listening...";
    try {
      recognition.start();
    } catch (e) {
      console.error("[ERROR] Failed to start recognition:", e);
      appendMessage("System", "Failed to start microphone");
    }
  }
});

initAvatar(canvas);

// const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}:8000/ws`;
const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;


startBtn.addEventListener("click", () => {
  // Show consent modal first
  if (!consentGiven) {
    consentModal.classList.remove("hidden");
  } else {
    // If consent already given, connect directly
    connect();
  }
});
endBtn.addEventListener("click", () => disconnect());
continuousBtn.addEventListener("click", () => {
  continuousMode = !continuousMode;
  if (continuousMode) {
    continuousBtn.style.background = "#10b981";
    continuousBtn.style.borderColor = "#059669";
    continuousBtn.style.color = "#fff";
    appendMessage("System", "🔄 Continuous mode enabled - Mic will auto-activate after each AI response");
  } else {
    continuousBtn.style.background = "";
    continuousBtn.style.borderColor = "";
    continuousBtn.style.color = "";
    appendMessage("System", "Continuous mode disabled");
  }
});

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  console.log("[DEBUG] Form submit:", text, "connected:", connected, "waiting:", waitingForAI);
  if (!text || !connected || waitingForAI) return;
  sendUserMessage(text);
  inputEl.value = "";
});

function connect() {
  if (connected || connecting) return;
  connecting = true;
  handshakeComplete = false;
  setStartButtonState("connecting");
  console.log("[DEBUG] Connecting to WebSocket:", wsUrl);
  ws = new WebSocket(wsUrl);

  // Fail if not connected within 8 seconds
  connectTimeout = setTimeout(() => {
    if (!handshakeComplete && ws && ws.readyState !== WebSocket.OPEN) {
      console.error("[ERROR] WebSocket connection timeout");
      ws.close();
      connecting = false;
      setStartButtonState("idle");
      alert("Unable to connect to interview server. Please try again.");
    }
  }, 8000);

  ws.onopen = () => {
    handshakeComplete = true;
    clearTimeout(connectTimeout);
    connected = true;
    connecting = false;
    interviewStarted = false;
    waitingForAI = false;
    connectionLabel.textContent = "connected";
    setStartButtonState("connected");
    endBtn.disabled = false;
    
    // Start observation polling (camera already started on page load)
    observation.startPolling(250); // Poll every 250ms for faster response (4 FPS)
    observation.onObservation = (result) => {
      // result contains {observation, warnings}
      if (result.observation) {
        updateObservationMetrics(result.observation);
      }
      if (result.warnings && result.warnings.length > 0) {
        displayWarnings(result.warnings);
      } else {
        clearWarnings();
      }
    };
    console.log("[DEBUG] Observation polling started");
    
    console.log("[DEBUG] WebSocket connected, waiting for greeting...");
  };
  ws.onmessage = (event) => {
    console.log("[DEBUG] WebSocket message received:", event.data.substring(0, 100));
    try {
      const payload = JSON.parse(event.data);
      handleAiMessage(payload);
    } catch (e) {
      console.error("[ERROR] Failed to parse WebSocket message:", e);
    }
  };
  ws.onclose = () => {
    clearTimeout(connectTimeout);
    endBtn.disabled = true;
    if (connected) {
      connected = false;
      interviewStarted = false;
      waitingForAI = false;
      handshakeComplete = false;
      connectionLabel.textContent = "disconnected";
      setStartButtonState("idle");
      stopMouth();
      
      // Stop observation
      observation.stopObservation().then(() => {
        observation.stopPolling();
        // Show final report
        showObservationReport();
      });
      
      console.log("[DEBUG] WebSocket disconnected");
    } else {
      // Disconnected during connection attempt
      connecting = false;
      setStartButtonState("idle");
      connectionLabel.textContent = "disconnected";
      console.error("[ERROR] WebSocket disconnected before handshake");
      alert("Unable to connect to interview server. Please try again.");
    }
  };
  ws.onerror = (error) => {
    console.error("[ERROR] WebSocket error:", error);
    clearTimeout(connectTimeout);
    if (!handshakeComplete) {
      connecting = false;
      setStartButtonState("idle");
      alert("Unable to connect to interview server. Please try again.");
    }
    appendMessage("System", "WebSocket error - check if backend is running");
  };
}

function disconnect() {
  if (ws && connected) {
    console.log("[DEBUG] Disconnecting and showing report...");
    ws.close();
    connected = false;
    interviewStarted = false;
    waitingForAI = false;
    handshakeComplete = false;
    connecting = false;
    setStartButtonState("idle");
    endBtn.disabled = true;
    
    // Stop observation and show report
    observation.stopObservation().then(() => {
      observation.stopPolling();
      console.log("[DEBUG] Showing final report...");
      showObservationReport();
    });
  }
}

function sendUserMessage(text) {
  console.log("[DEBUG] Sending user message:", text);
  appendMessage("You", text, "user");
  ws.send(JSON.stringify({ text }));
  waitingForAI = true;
  inputEl.disabled = true;
  speakBtn.disabled = true;
}

function handleAiMessage(payload) {
  const response = payload.interviewer_response || "";
  const state = payload.system_state || "WARM_UP";
  
  console.log("[DEBUG] Handling AI message - State:", state, "Response:", response.substring(0, 50));
  
  stageLabel.textContent = state;
  avatarStateLabel.textContent = payload.avatar_state || "neutral_listening";
  setAvatarState(payload.avatar_state || "neutral_listening");
  appendMessage("AI", response, "ai");
  
  waitingForAI = false;

  // Handle different interview states
  if (state === "GREETING") {
    interviewStarted = false;
    inputEl.disabled = false;
    formEl.querySelector("button[type='submit']").disabled = false;
    speakBtn.disabled = false;
    inputEl.placeholder = "Say 'hello' or 'ready' to begin...";
  } else if (state === "CLOSURE") {
    interviewStarted = false;
    continuousMode = false;
    inputEl.disabled = true;
    formEl.querySelector("button[type='submit']").disabled = true;
    speakBtn.disabled = true;
    appendMessage("System", "Interview completed. Thank you!");
  } else {
    interviewStarted = true;
    inputEl.disabled = false;
    formEl.querySelector("button[type='submit']").disabled = false;
    speakBtn.disabled = false;
  }

  if (payload.tts_enabled) {
    speak(response);
  }
}

// Expose for manual testing via console
window.handleAiMessage = handleAiMessage;

function appendMessage(speaker, text, role = "ai") {
  console.log("[DEBUG] Appending message:", speaker, text.substring(0, 30));
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = `<strong>${speaker}:</strong> ${text}`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function speak(text) {
  if (!window.speechSynthesis) {
    console.warn("[WARNING] Speech synthesis not available");
    return;
  }
  console.log("[DEBUG] Speaking:", text.substring(0, 50));
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.onstart = () => {
    speechActive = true;
    startMouth();
  };
  utterance.onend = () => {
    speechActive = false;
    stopMouth();
    
    // Auto-activate mic in continuous mode after AI finishes
    if (continuousMode && interviewStarted && !isListening && recognition) {
      console.log("[DEBUG] Continuous mode: auto-activating mic");
      setTimeout(() => {
        if (!isListening && connected && interviewStarted && !waitingForAI) {
          playBuzzer();
          inputEl.value = "";
          inputEl.placeholder = "🎙️ Listening...";
          try {
            recognition.start();
          } catch (e) {
            console.error("[ERROR] Auto-mic failed:", e);
          }
        }
      }, 800);
    }
  };
  utterance.onerror = () => {
    speechActive = false;
    stopMouth();
    console.error("[ERROR] Speech synthesis error");
  };
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

/**
 * Start audio visualization - now shows speaking indicator
 */
function startAudioVisualization() {
  if (!observation.mediaStream) {
    console.error("[ERROR] No media stream available for visualization");
    return;
  }
  
  try {
    console.log("[DEBUG] Starting audio visualization...");
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(observation.mediaStream);
    audioAnalyzer = audioContext.createAnalyser();
    audioAnalyzer.fftSize = 256;
    audioAnalyzer.smoothingTimeConstant = 0.7;
    source.connect(audioAnalyzer);
    
    const bufferLength = audioAnalyzer.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    console.log("[DEBUG] Audio analyzer initialized, buffer length:", bufferLength);
    
    let frameCount = 0;
    function draw() {
      if (!consentGiven) return;
      audioAnimationFrame = requestAnimationFrame(draw);
      
      audioAnalyzer.getByteFrequencyData(dataArray);
      
      // Calculate average amplitude
      let avgAmplitude = 0;
      for (let i = 0; i < bufferLength; i++) {
        avgAmplitude += dataArray[i];
      }
      avgAmplitude = avgAmplitude / bufferLength;
      
      // Show speaking indicator if audio is detected
      if (avgAmplitude > 30) {
        speakingIndicator.style.display = "flex";
      } else {
        speakingIndicator.style.display = "none";
      }
      
      // Log audio activity every 30 frames
      frameCount++;
      if (frameCount % 30 === 0) {
        console.log(`[AUDIO] Average amplitude: ${avgAmplitude.toFixed(1)}, Speaking: ${avgAmplitude > 30 ? 'YES' : 'NO'}`);
      }
    }
    
    draw();
    console.log("[DEBUG] Audio visualization drawing loop started");
  } catch (err) {
    console.error("[ERROR] Audio visualization failed:", err);
  }
}

/**
 * Display violation warnings
 */
function displayWarnings(warnings) {
  const warningsContainer = document.getElementById("warnings-container");
  if (!warningsContainer) {
    console.error("[WARNING] warnings-container element not found in DOM");
    return;
  }
  
  if (!warnings || warnings.length === 0) {
    warningsContainer.innerHTML = "";
    return;
  }
  
  // Clear existing warnings
  warningsContainer.innerHTML = "";
  
  console.log(`[WARNINGS] Displaying ${warnings.length} warning(s)`, warnings);
  
  // Add each warning
  warnings.forEach((warning, index) => {
    const warningEl = document.createElement("div");
    warningEl.className = `warning warning-${(warning.severity || "warning").toLowerCase()}`;
    warningEl.innerHTML = `
      <span class="warning-icon">${warning.icon || '⚠️'}</span>
      <span class="warning-message">${warning.message || 'Unknown warning'}</span>
    `;
    warningsContainer.appendChild(warningEl);
    console.log(`[WARNINGS] Added warning ${index + 1}: ${warning.type} - ${warning.message}`);
  });
}

/**
 * Clear all warnings
 */
function clearWarnings() {
  const warningsContainer = document.getElementById("warnings-container");
  if (warningsContainer) {
    warningsContainer.innerHTML = "";
  }
}

/**
 * Update observation metrics display
 */
/**
 * Update observation metrics display
 */
function updateObservationMetrics(observation) {
  if (!observation) return;

  // Extract metrics from observation
  const audio = observation.audio || {};
  const emotion = observation.emotion || {};
  const face = observation.face || {};

  // Eye contact score (based on looking_at_camera + confidence)
  const eyeContactEl = document.getElementById("metric-eye-contact");
  const eyeContactBar = document.getElementById("metric-eye-contact-bar");
  if (eyeContactEl) {
    if (!face.face_detected) {
      eyeContactEl.textContent = "—";
      if (eyeContactBar) eyeContactBar.style.width = "0%";
    } else {
      const confidence = face.eye_contact_confidence || 0;
      const score = Math.round(confidence * 10);
      eyeContactEl.textContent = score;
      if (eyeContactBar) eyeContactBar.style.width = `${confidence * 100}%`;
    }
  }

  // Focus score
  const focusEl = document.getElementById("metric-focus");
  const focusBar = document.getElementById("metric-focus-bar");
  if (focusEl) {
    const focusScore = face.looking_away ? 3 : (face.looking_at_camera ? 9 : 6);
    focusEl.textContent = focusScore;
    if (focusBar) focusBar.style.width = `${(focusScore / 10) * 100}%`;
  }

  // Stress level
  const stressEl = document.getElementById("metric-stress");
  const stressBar = document.getElementById("metric-stress-bar");
  if (stressEl) {
    const stress = audio.stress_level || emotion.stress_level || "low";
    stressEl.textContent = stress === "calibrating" ? "calibrating" : stress;
    if (stressBar) {
      const stressNumeric = stress === "high" ? 8 : stress === "medium" ? 5 : 2;
      stressBar.style.width = `${(stressNumeric / 10) * 100}%`;
    }
  }

  // Voice confidence
  const voiceEl = document.getElementById("metric-voice");
  const voiceBar = document.getElementById("metric-voice-bar");
  if (voiceEl) {
    const voice = audio.voice_confidence !== undefined ? audio.voice_confidence : null;
    if (voice !== null && voice >= 0) {
      const score = Math.round(voice * 10);
      voiceEl.textContent = score;
      if (voiceBar) voiceBar.style.width = `${voice * 100}%`;
    } else {
      voiceEl.textContent = "—";
      if (voiceBar) voiceBar.style.width = "0%";
    }
  }
}

/**
 * Display final observation report when interview ends
 */
async function showObservationReport() {
  console.log("[INFO] Fetching observation report...");
  const report = await observation.getReport();
  
  if (!report) {
    console.log("[INFO] No observation report available");
    appendMessage("System", "Interview ended. No behavioral data collected.", "ai");
    return;
  }

  console.log("[INFO] Observation Report:", report);

  // Create detailed report message
  const reportMsg = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 BEHAVIORAL ANALYSIS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 PERFORMANCE SCORES:
• Eye Contact: ${report.eye_contact_score || 0}/10
• Focus Level: ${report.focus_score || 0}/10
• Stress Management: ${report.stress_level || 'N/A'}
• Voice Confidence: ${report.voice_confidence || 0}/10

✅ STRENGTHS:
${(report.behavioral_strengths || []).map(s => `  • ${s}`).join('\n') || '  • No data available'}

📌 AREAS FOR IMPROVEMENT:
${(report.behavioral_improvements || []).map(i => `  • ${i}`).join('\n') || '  • No data available'}

🎯 OVERALL READINESS: ${report.overall_interview_readiness || 'N/A'}

⏱️  Session Duration: ${Math.round(report.session_duration || 0)}s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  `.trim();

  appendMessage("Behavioral Analysis", reportMsg, "ai");
  
  // Also log to console for debugging
  console.log("[REPORT] Full data:", JSON.stringify(report, null, 2));
}

