import * as THREE from "https://esm.sh/three@0.158.0";
import { GLTFLoader } from "https://esm.sh/three@0.158.0/examples/jsm/loaders/GLTFLoader.js";

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

export function initAvatar(canvas) {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf9fafb);
  
  camera = new THREE.PerspectiveCamera(50, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
  camera.position.set(0, 0.5, 0.5);

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
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

  loader.load(
    "https://models.readyplayer.me/695a5b438f9c70cbc9271ff0.glb?morphTargets=ARKit,Oculus+Visemes&textureAtlas=1024",
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
            if (obj.material.color) {
              obj.material.color.setHex(0xffd0b0); // skin tone
            }
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
