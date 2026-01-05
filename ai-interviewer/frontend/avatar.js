import * as THREE from "https://esm.sh/three@0.158.0";
import { GLTFLoader } from "https://esm.sh/three@0.158.0/examples/jsm/loaders/GLTFLoader.js";

// Avatar model URLs for Jai, Chey, Sree
const AVATAR_MODELS = [
  "https://models.readyplayer.me/695b9b4d1c1817592c44c47e.glb?morphTargets=ARKit,Oculus+Visemes&textureAtlas=1024", // Jai
  "https://models.readyplayer.me/695b9c91e2b2692fdd9978a5.glb?morphTargets=ARKit,Oculus+Visemes&textureAtlas=1024", // Chey
  "https://models.readyplayer.me/695ba8cf452afe2bbfb84647.glb?morphTargets=ARKit,Oculus+Visemes&textureAtlas=1024"  // Sree
];

// Store state per canvas/avatar instance
const avatarInstances = new Map();

// Default global state for backward compatibility (single avatar mode)
let renderer;
let scene;
let camera;
let avatar;
let faceMesh;
let headBone;
let frameId;
let mouthTimer;
let eyeBlinkTimer;
let currentState = "neutral_listening";
let morphTargets = {};
let visemeOrder = ["viseme_aa", "viseme_ee", "viseme_oh", "viseme_sil"];
let blinkActive = false;
let nodPhase = 0;

// Avatar instance class
class AvatarInstance {
  constructor(canvas) {
    this.canvas = canvas;
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.avatar = null;
    this.faceMesh = null;
    this.headBone = null;
    this.frameId = null;
    this.mouthTimer = null;
    this.eyeBlinkTimer = null;
    this.currentState = "neutral_listening";
    this.morphTargets = {};
    this.visemeOrder = ["viseme_aa", "viseme_ee", "viseme_oh", "viseme_sil"];
    this.blinkActive = false;
    this.nodPhase = 0;
  }

  init() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf9fafb);
    
    this.camera = new THREE.PerspectiveCamera(50, this.canvas.clientWidth / this.canvas.clientHeight, 0.1, 100);
    this.camera.position.set(0, 0.5, 0.5);

    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: false });
    this.renderer.outputEncoding = THREE.sRGBEncoding; // keep colors true to texture
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.resize();

    // Lighting for realistic shading
    const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
    dirLight.position.set(2, 4, 5);
    this.scene.add(dirLight);
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.8);
    fillLight.position.set(-2, 0, 3);
    this.scene.add(fillLight);
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.8));

    // Load realistic human avatar (.glb with morph targets)
    const loader = new GLTFLoader();
    loader.setCrossOrigin("anonymous");

    // Get avatar index from canvas ID (avatar-canvas-0, avatar-canvas-1, etc.)
    const match = this.canvas.id.match(/avatar-canvas-(\d+)/);
    const avatarIndex = match ? parseInt(match[1]) : 0;
    const modelUrl = AVATAR_MODELS[avatarIndex % AVATAR_MODELS.length];

    loader.load(
      modelUrl,
      (gltf) => {
        this.avatar = gltf.scene;

        // Normalize per-model framing so all avatars sit at the same vertical level
        const scale = new THREE.Vector3(1.4, 1.25, 0.8);
        let yOffset = -1.6;
        if (avatarIndex === 1) {
          // Chey model rides a bit low; lift and slightly reduce scale to match others
          scale.set(1.35, 1.3, 0.8);
          yOffset = -1.48;
        }

        this.avatar.scale.copy(scale);
        this.avatar.position.set(0, yOffset, 0);
        this.scene.add(this.avatar);

        this.avatar.traverse((obj) => {
          if (obj.isMesh) {
            obj.castShadow = false;
            obj.receiveShadow = false;
            // Ensure material is properly lit
            if (obj.material) {
              obj.material.needsUpdate = true;
            }
            if (obj.morphTargetDictionary && obj.morphTargetInfluences) {
              console.log("Available morph targets:", Object.keys(obj.morphTargetDictionary));
              this.faceMesh = obj;
              // cache morph target indices
              Object.entries(obj.morphTargetDictionary).forEach(([key, idx]) => {
                this.morphTargets[key] = idx;
              });
              
              // LeePerrySmith has limited/no morph targets - log warning
              const morphCount = Object.keys(obj.morphTargetDictionary).length;
              if (morphCount === 0) {
                console.warn("⚠️ This model has NO morph targets. Eyes/lips cannot animate.");
                console.warn("💡 Use a ReadyPlayerMe avatar for full facial animation support.");
              } else {
                console.log(`✅ Found ${morphCount} morph targets`);
              }
            }
          }
          if (obj.isBone && obj.name.toLowerCase().includes("head")) {
            this.headBone = obj;
          }
        });

        this.canvas.addEventListener("resize", () => this.resize());
        this.animate();
        this.startBlinking();
      },
      undefined,
      (err) => {
        console.error("Avatar load failed:", err);
        this.createPlaceholder();
      }
    );
  }

  createPlaceholder() {
    this.avatar = new THREE.Group();
    const headGeo = new THREE.SphereGeometry(0.6, 32, 32);
    const headMat = new THREE.MeshStandardMaterial({ color: 0xd9c3a0, roughness: 0.5, metalness: 0 });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 0.4;
    const bodyGeo = new THREE.CylinderGeometry(0.55, 0.7, 1.6, 24);
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x4b5563, roughness: 0.7, metalness: 0.05 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = -0.9;
    this.avatar.add(head);
    this.avatar.add(body);
    this.avatar.position.set(0, -1.2, 0);
    this.scene.add(this.avatar);
    this.canvas.addEventListener("resize", () => this.resize());
    this.animate();
  }

  resize() {
    if (!this.renderer || !this.camera) return;
    const { clientWidth, clientHeight } = this.canvas;
    this.camera.aspect = clientWidth / clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(clientWidth, clientHeight, false);
  }

  animate = () => {
    this.frameId = requestAnimationFrame(this.animate);
    if (this.avatar) {
      const t = Date.now() * 0.0004;
      
      // More natural head movement - slight side to side sway
      const sway = Math.sin(t) * 0.08;
      this.avatar.rotation.y = sway;
      
      // Subtle bobbing motion
      const bobAmount = Math.cos(t * 0.5) * 0.02;
      this.avatar.position.y = -1.6 + bobAmount;
      
      // Add more expressive head movement during speech
      if (this.currentState === "speaking" && this.headBone) {
        // More pronounced nodding during speech
        this.nodPhase += 0.06;
        this.headBone.rotation.x = -0.08 + Math.sin(this.nodPhase) * 0.05;
        this.headBone.rotation.z = Math.sin(this.nodPhase * 0.5) * 0.04; // Slight head tilt
      } else if (this.currentState === "attentive_nod" && this.headBone) {
        this.nodPhase += 0.04;
        this.headBone.rotation.x = -0.05 + Math.sin(this.nodPhase) * 0.03;
      } else if (this.headBone) {
        // Return to neutral position smoothly
        this.headBone.rotation.x = THREE.MathUtils.lerp(this.headBone.rotation.x, 0, 0.1);
        this.headBone.rotation.z = THREE.MathUtils.lerp(this.headBone.rotation.z, 0, 0.1);
      }
      
      // head tilt for thinking (slight side tilt)
      if (this.currentState === "thinking" && this.headBone) {
        this.headBone.rotation.z = THREE.MathUtils.lerp(this.headBone.rotation.z, 0.08, 0.1);
      } else if (this.headBone && this.currentState !== "speaking") {
        this.headBone.rotation.z = THREE.MathUtils.lerp(this.headBone.rotation.z, 0, 0.1);
      }
    }
    this.renderer.render(this.scene, this.camera);
  }

  startBlinking() {
    this.eyeBlinkTimer = setInterval(() => {
      this.blink();
    }, Math.random() * 4000 + 3000); // Blink every 3-7 seconds
  }

  blink() {
    if (!this.faceMesh || this.blinkActive) return;
    this.blinkActive = true;
    this.setMorph("eyeBlinkLeft", 0.9);
    this.setMorph("eyeBlinkRight", 0.9);
    setTimeout(() => {
      this.setMorph("eyeBlinkLeft", 0);
      this.setMorph("eyeBlinkRight", 0);
      this.blinkActive = false;
    }, 160);
  }

  setState(state) {
    this.currentState = state;
    if (!this.faceMesh) return;

    // reset base expressions
    this.setMorph("browInnerUp", 0);
    this.setMorph("browDown", 0);
    this.setMorph("mouthSmile", 0);
    this.setMorph("eyeBlinkLeft", 0);
    this.setMorph("eyeBlinkRight", 0);

    switch (state) {
      case "neutral_listening":
        // neutral baseline, blinking handled separately
        break;
      case "attentive_nod":
        this.setMorph("mouthSmile", 0.25);
        break;
      case "thinking":
        this.setMorph("browInnerUp", 0.35);
        break;
      case "confused":
        this.setMorph("browDown", 0.35);
        this.setMorph("mouthSmile", 0.05);
        break;
      case "mildly_impressed":
        this.setMorph("mouthSmile", 0.35);
        break;
      case "pressure_mode":
        this.setMorph("eyeBlinkLeft", 0.05);
        this.setMorph("eyeBlinkRight", 0.05);
        break;
      case "concluding":
        this.setMorph("mouthSmile", 0.4);
        break;
      case "smiling":
        this.setMorph("mouthSmile", 0.45);
        break;
      default:
        break;
    }
  }

  startMouth() {
    if (!this.faceMesh) return;
    this.stopMouth();
    
    // Set state to speaking for head movement animation
    this.currentState = "speaking";
    
    let visemeIdx = 0;
    let lastViseme = null;
    
    this.mouthTimer = setInterval(() => {
      // Try standard viseme targets first
      if ("viseme_aa" in this.morphTargets || "viseme_AA" in this.morphTargets) {
        // Vary mouth movement more naturally
        const visemeSequence = ["viseme_aa", "viseme_ee", "viseme_oh", "viseme_sil", "viseme_ee", "viseme_aa"];
        const currentViseme = visemeSequence[visemeIdx % visemeSequence.length];
        
        // Reset all visemes
        this.setMorph("viseme_aa", 0);
        this.setMorph("viseme_ee", 0);
        this.setMorph("viseme_oh", 0);
        this.setMorph("viseme_sil", 0);
        
        // Set current with varying intensity
        const intensity = 0.5 + Math.random() * 0.35; // Random intensity 0.5-0.85
        this.setMorph(currentViseme, intensity);
        
        visemeIdx += 1;
      } else {
        // Fallback: generic jaw/mouth opening animation with more natural motion
        const t = Date.now() * 0.008;
        const baseOpen = (Math.sin(t) * 0.5 + 0.5) * 0.35;
        const noise = Math.random() * 0.1;
        const openAmount = Math.min(0.45, baseOpen + noise);
        
        // Try common morph target names for mouth/jaw
        this.setMorph("mouthOpen", openAmount);
        this.setMorph("jawOpen", openAmount);
        this.setMorph("mouth_open", openAmount);
      }
    }, 60); // Faster update for smoother lip sync
  }

  stopMouth() {
    if (this.mouthTimer) {
      clearInterval(this.mouthTimer);
      this.mouthTimer = undefined;
    }
    
    // Reset state to neutral
    this.currentState = "neutral_listening";
    
    // Smooth reset of all visemes
    this.setMorph("viseme_aa", 0);
    this.setMorph("viseme_ee", 0);
    this.setMorph("viseme_oh", 0);
    this.setMorph("viseme_sil", 0);
    this.setMorph("mouthOpen", 0);
    this.setMorph("jawOpen", 0);
    this.setMorph("mouth_open", 0);
  }

  dispose() {
    cancelAnimationFrame(this.frameId);
    this.stopMouth();
    this.renderer?.dispose();
    this.scene = undefined;
    this.camera = undefined;
    this.avatar = undefined;
    this.faceMesh = undefined;
    this.headBone = undefined;
  }

  setMorph(name, value) {
    if (!this.faceMesh || !(name in this.morphTargets)) {
      return;
    }
    const idx = this.morphTargets[name];
    this.faceMesh.morphTargetInfluences[idx] = THREE.MathUtils.lerp(
      this.faceMesh.morphTargetInfluences[idx] || 0,
      value,
      0.4
    );
  }
}

export function initAvatar(canvas) {
  // Check if this is a multi-avatar scenario
  if (canvas.id && canvas.id.startsWith("avatar-canvas-")) {
    // Multi-avatar mode: create instance
    const instance = new AvatarInstance(canvas);
    avatarInstances.set(canvas.id, instance);
    instance.init();
    return;
  }

  // Single avatar mode (backward compatibility)
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf9fafb);
  
  camera = new THREE.PerspectiveCamera(50, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
  camera.position.set(0, 0.5, 0.5);

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.outputEncoding = THREE.sRGBEncoding; // preserve texture color accuracy
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.setPixelRatio(window.devicePixelRatio);
  resize(canvas);

  // Lighting for realistic shading
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
  dirLight.position.set(2, 4, 5);
  scene.add(dirLight);
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.8);
  fillLight.position.set(-2, 0, 3);
  scene.add(fillLight);
  scene.add(new THREE.AmbientLight(0xffffff, 0.8));

  // Load realistic human avatar (.glb with morph targets)
  const loader = new GLTFLoader();
  loader.setCrossOrigin("anonymous");

  // Use first avatar (Jai) for backward compatibility single avatar mode
  const modelUrl = AVATAR_MODELS[0];

  loader.load(
    modelUrl,
    (gltf) => {
      avatar = gltf.scene;
      avatar.scale.set(1.4, 1.3, 0.8);
      avatar.position.set(0, -1.6, 0);
      scene.add(avatar);

      avatar.traverse((obj) => {
        if (obj.isMesh) {
          obj.castShadow = false;
          obj.receiveShadow = false;
          // Ensure material is properly lit
          if (obj.material) {
            obj.material.needsUpdate = true;
          }
          if (obj.morphTargetDictionary && obj.morphTargetInfluences) {
            console.log("Available morph targets:", Object.keys(obj.morphTargetDictionary));
            faceMesh = obj;
            // cache morph target indices
            Object.entries(obj.morphTargetDictionary).forEach(([key, idx]) => {
              morphTargets[key] = idx;
            });
            
            // LeePerrySmith has limited/no morph targets - log warning
            const morphCount = Object.keys(obj.morphTargetDictionary).length;
            if (morphCount === 0) {
              console.warn("⚠️ This model has NO morph targets. Eyes/lips cannot animate.");
              console.warn("💡 Use a ReadyPlayerMe avatar for full facial animation support.");
            } else {
              console.log(`✅ Found ${morphCount} morph targets`);
            }
          }
        }
        if (obj.isBone && obj.name.toLowerCase().includes("head")) {
          headBone = obj;
        }
      });

      window.addEventListener("resize", () => resize(canvas));
      animate();
      startBlinking();
    },
    undefined,
    (err) => {
      console.error("Avatar load failed:", err);
      createPlaceholderAvatar();
    }
  );
}

function createPlaceholderAvatar() {
  avatar = new THREE.Group();
  const headGeo = new THREE.SphereGeometry(0.6, 32, 32);
  const headMat = new THREE.MeshStandardMaterial({ color: 0xd9c3a0, roughness: 0.5, metalness: 0 });
  const head = new THREE.Mesh(headGeo, headMat);
  head.position.y = 0.4;
  const bodyGeo = new THREE.CylinderGeometry(0.55, 0.7, 1.6, 24);
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0x4b5563, roughness: 0.7, metalness: 0.05 });
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.position.y = -0.9;
  avatar.add(head);
  avatar.add(body);
  avatar.position.set(0, -1.2, 0);
  scene.add(avatar);
  window.addEventListener("resize", () => resize(renderer.domElement));
  animate();
}

function resize(canvas) {
  if (!renderer || !camera) return;
  const { clientWidth, clientHeight } = canvas;
  camera.aspect = clientWidth / clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(clientWidth, clientHeight, false);
}

function animate() {
  frameId = requestAnimationFrame(animate);
  if (avatar) {
    const t = Date.now() * 0.0004;
    avatar.rotation.y = Math.sin(t) * 0.05;
    avatar.position.y = -1.6 + Math.cos(t * 0.5) * 0.01;
    // gentle nod when attentive
    if (currentState === "attentive_nod" && headBone) {
      nodPhase += 0.04;
      headBone.rotation.x = -0.05 + Math.sin(nodPhase) * 0.03;
    } else if (headBone) {
      headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, 0, 0.1);
    }
    // head tilt for thinking
    if (currentState === "thinking" && headBone) {
      headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, 0.08, 0.1);
    } else if (headBone) {
      headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, 0, 0.1);
    }
  }
  renderer.render(scene, camera);
}

function startBlinking() {
  eyeBlinkTimer = setInterval(() => {
    blink();
  }, Math.random() * 4000 + 3000); // Blink every 3-7 seconds
}

function blink() {
  if (!faceMesh || blinkActive) return;
  blinkActive = true;
  setMorph("eyeBlinkLeft", 0.9);
  setMorph("eyeBlinkRight", 0.9);
  setTimeout(() => {
    setMorph("eyeBlinkLeft", 0);
    setMorph("eyeBlinkRight", 0);
    blinkActive = false;
  }, 160);
}

export function setAvatarState(state) {
  currentState = state;
  if (!faceMesh) return;

  // reset base expressions
  setMorph("browInnerUp", 0);
  setMorph("browDown", 0);
  setMorph("mouthSmile", 0);
  setMorph("eyeBlinkLeft", 0);
  setMorph("eyeBlinkRight", 0);

  switch (state) {
    case "neutral_listening":
      // neutral baseline, blinking handled separately
      break;
    case "attentive_nod":
      setMorph("mouthSmile", 0.25);
      break;
    case "thinking":
      setMorph("browInnerUp", 0.35);
      break;
    case "confused":
      setMorph("browDown", 0.35);
      setMorph("mouthSmile", 0.05);
      break;
    case "mildly_impressed":
      setMorph("mouthSmile", 0.35);
      break;
    case "pressure_mode":
      setMorph("eyeBlinkLeft", 0.05);
      setMorph("eyeBlinkRight", 0.05);
      break;
    case "concluding":
      setMorph("mouthSmile", 0.4);
      break;
    case "smiling":
      setMorph("mouthSmile", 0.45);
      break;
    default:
      break;
  }
}

export function startMouth() {
  if (!faceMesh) return;
  stopMouth();
  let visemeIdx = 0;
  mouthTimer = setInterval(() => {
    // Try standard viseme targets first
    if ("viseme_aa" in morphTargets || "viseme_AA" in morphTargets) {
      const currentViseme = visemeOrder[visemeIdx % visemeOrder.length];
      visemeIdx += 1;
      setMorph("viseme_aa", 0);
      setMorph("viseme_ee", 0);
      setMorph("viseme_oh", 0);
      setMorph("viseme_sil", 0);
      setMorph(currentViseme, 0.65);
    } else {
      // Fallback: generic jaw/mouth opening animation
      const t = Date.now() * 0.01;
      const openAmount = (Math.sin(t) * 0.5 + 0.5) * 0.3;
      // Try common morph target names for mouth/jaw
      setMorph("mouthOpen", openAmount);
      setMorph("jawOpen", openAmount);
      setMorph("mouth_open", openAmount);
    }
  }, 90);
}

export function stopMouth() {
  if (mouthTimer) {
    clearInterval(mouthTimer);
    mouthTimer = undefined;
  }
  setMorph("viseme_aa", 0);
  setMorph("viseme_ee", 0);
  setMorph("viseme_oh", 0);
  setMorph("viseme_sil", 0);
}

export function disposeAvatar() {
  cancelAnimationFrame(frameId);
  stopMouth();
  renderer?.dispose();
  scene = undefined;
  camera = undefined;
  avatar = undefined;
  faceMesh = undefined;
  headBone = undefined;
}

function setMorph(name, value) {
  if (!faceMesh || !(name in morphTargets)) {
    return;
  }
  const idx = morphTargets[name];
  faceMesh.morphTargetInfluences[idx] = THREE.MathUtils.lerp(
    faceMesh.morphTargetInfluences[idx] || 0,
    value,
    0.4
  );
}

/**
 * Start mouth animation for a specific avatar instance
 */
export function startMouthForAvatar(avatarIndex) {
  const instance = avatarInstances.get(`avatar-canvas-${avatarIndex}`);
  if (instance) {
    instance.startMouth();
  }
}

/**
 * Stop mouth animation for a specific avatar instance
 */
export function stopMouthForAvatar(avatarIndex) {
  const instance = avatarInstances.get(`avatar-canvas-${avatarIndex}`);
  if (instance) {
    instance.stopMouth();
  }
}
