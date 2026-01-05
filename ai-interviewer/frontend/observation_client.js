/**
 * Observation Client
 * Communicates with backend observation engine
 */

export class ObservationClient {
  constructor(backendUrl = window.location.origin) {
// constructor(backendUrl = "http://localhost:8000") { // For local testing
    this.backendUrl = backendUrl;
    this.running = false;
    this.videoElement = null;
    this.mediaStream = null;
    this.onObservation = null;
  }

  async startObservation() {
    try {
      // Request user's camera FIRST
      try {
        console.log("[ObservationClient] Requesting camera access...");
        this.mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480, facingMode: "user" },
          audio: true
        });
        console.log("[ObservationClient] Camera access granted, stream:", this.mediaStream);

        if (this.videoElement) {
          console.log("[ObservationClient] Setting video srcObject...");
          this.videoElement.srcObject = this.mediaStream;
          
          // Immediately try to play
          try {
            await this.videoElement.play();
            console.log("[ObservationClient] Video playing successfully");
          } catch (playErr) {
            console.warn("[ObservationClient] Immediate play failed, waiting for metadata:", playErr);
            // Wait for metadata and try again
            this.videoElement.onloadedmetadata = async () => {
              try {
                await this.videoElement.play();
                console.log("[ObservationClient] Video playing after metadata loaded");
              } catch (err) {
                console.error("[ObservationClient] Video play failed:", err);
              }
            };
          }
        } else {
          console.error("[ObservationClient] Video element is null!");
        }
      } catch (err) {
        console.error("[ObservationClient] Camera access denied:", err);
        throw err;
      }

      // Start backend observation engine
      try {
        const startRes = await fetch(`${this.backendUrl}/observation/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        const startData = await startRes.json();
        
        if (!startData.success) {
          console.error("[ObservationClient] Backend observation failed to start");
        }
      } catch (err) {
        console.error("[ObservationClient] Backend observation error:", err);
      }

      this.running = true;
      
      // Start sending video frames to backend for analysis
      this.startVideoFrameCapture();
      
      console.log("[ObservationClient] Observation started successfully");
      return true;
    } catch (err) {
      console.error("[ObservationClient] Failed to start observation:", err);
      return false;
    }
  }
  
  startVideoFrameCapture() {
    // Send video frames to backend for analysis
    if (!this.videoElement || !this.running) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 640;
    canvas.height = 480;
    
    const captureFrame = async () => {
      if (!this.running || !this.videoElement) return;
      
      try {
        // Draw current video frame to canvas
        ctx.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64 JPEG (0.7 quality for faster encoding)
        const frameData = canvas.toDataURL('image/jpeg', 0.7).split(',')[1];
        
        // Send to backend asynchronously (don't wait for response)
        fetch(`${this.backendUrl}/observation/add_video_frame`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ frame_data: frameData })
        }).catch(err => {
          if (Math.random() < 0.1) { // Log 10% of errors to avoid spam
            console.error('[ObservationClient] Frame capture error:', err);
          }
        });
        
      } catch (err) {
        if (Math.random() < 0.1) {
          console.error('[ObservationClient] Frame encoding error:', err);
        }
      }
      
      // Capture at 6 FPS = every ~167ms for faster response
      if (this.running) {
        setTimeout(captureFrame, 167);
      }
    };
    
    // Start capture loop after video stabilizes
    setTimeout(captureFrame, 800);
  }

  async stopObservation() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }

    try {
      await fetch(`${this.backendUrl}/observation/stop`, { method: "POST" });
    } catch (err) {
      console.error("[ObservationClient] Error stopping observation:", err);
    }

    this.running = false;
    console.log("[ObservationClient] Observation stopped");
  }

  async getLatestObservation() {
    try {
      const res = await fetch(`${this.backendUrl}/observation/latest`);
      const data = await res.json();
      
      // Log warnings if present (5% sampling to avoid spam)
      if (Math.random() < 0.05 && data.warnings && data.warnings.length > 0) {
        console.log(`[ObservationClient] Warnings received:`, data.warnings);
      }
      
      return {
        observation: data.observation,
        warnings: data.warnings || []
      };
    } catch (err) {
      console.error("[ObservationClient] Error fetching observation:", err);
      return { observation: null, warnings: [] };
    }
  }

  async getReport() {
    try {
      const res = await fetch(`${this.backendUrl}/observation/report`);
      const data = await res.json();
      return data.report;
    } catch (err) {
      console.error("[ObservationClient] Error fetching report:", err);
      return null;
    }
  }

  async reset() {
    try {
      await fetch(`${this.backendUrl}/observation/reset`, { method: "POST" });
      console.log("[ObservationClient] Reset complete");
    } catch (err) {
      console.error("[ObservationClient] Error resetting:", err);
    }
  }

  startPolling(interval = 500) {
    /**Poll for observations every interval ms*/
    this.pollingInterval = setInterval(async () => {
      if (this.running) {
        const result = await this.getLatestObservation();
        if (result.observation && this.onObservation) {
          // Pass both observation and warnings
          this.onObservation({
            observation: result.observation,
            warnings: result.warnings
          });
        }
      }
    }, interval);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  setVideoElement(element) {
    this.videoElement = element;
  }
}
