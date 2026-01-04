# Quick Start Testing Guide

## How to Test All Fixes

### 1. Start the System
```bash
# Terminal 1 - Backend
cd d:\AI_interviewer\ai-interviewer\backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd d:\AI_interviewer\ai-interviewer\frontend
npx http-server --port 5500 --cors
```

### 2. Access the App
- Open browser: `http://localhost:5500`
- **IMPORTANT**: Hard refresh with `Ctrl+Shift+R` to clear CSS cache (for mirror view)
- Enable browser console: `F12` → Console tab to see debug logs

### 3. Test Each Feature

#### Test A: Eye Contact Display
1. Start interview
2. Look directly at camera → **Eye Contact should show 7-10/10 (green)**
3. Look slightly away → **Should drop to 4-6/10 (orange)**
4. Look far away → **Should drop to 0-3/10 (red)**
5. Console should show debug logs with confidence values

#### Test B: Warning for Looking Away
1. During interview, turn head left → **Orange ⚠️ warning should appear in <250ms**
2. Turn head right → **Warning should update**
3. Turn head back to camera → **Warning should disappear in <250ms**
4. Look down → **Warning appears**
5. Look up → **Warning appears**

#### Test C: Multiple Person Detection
1. During interview, move someone into frame
2. **Red 🚨 CRITICAL warning should appear immediately**
3. Move person out of frame
4. **Red warning disappears in <250ms**

#### Test D: Layout & Positioning
1. Start interview
2. Scroll conversation panel - Avatar and Camera panels should **stay fixed** (not move)
3. Camera panel should **not overlap** with conversation panel
4. Video should be **horizontally flipped** (mirror effect)

#### Test E: Performance
1. Check browser console (F12)
2. You should see debug logs approximately once per second
3. Debug log format: `[EYE_CONTACT] confidence=0.XXX, base=X, looking_at_camera=true/false, yaw=X.X°, pitch=X.X°`

### 4. Verify in Final Report
After interview ends, check the report:
- Eye Contact score should match real-time values (not 10/10 if you weren't looking)
- Focus score should reflect looking away time
- Emotion should show detected emotion (not "detecting...")
- Voice Confidence should be 5-10/10 (not 0/10)

## Debug Commands

### Check Python Logs
The backend logs will show:
```
[DEBUG] Processing video frame...
[INFO] Human Observation Engine initialized
```

### Check Frontend Console Logs
Press `F12` and look for:
```
[EYE_CONTACT] confidence=0.723, base=7, looking_at_camera=true, yaw=2.3°, pitch=-1.2°
[DEBUG] Observation polling started
[INFO] Audio visualization drawing loop started
```

## If Something Isn't Working

### Eye contact still shows 0
- Check F12 console for debug logs
- Verify `eye_contact_confidence` value being logged
- Make sure face is detected (check for "Face not detected" warning)

### Warnings not showing
- Check browser console for errors
- Verify warnings container is in HTML: `<div id="warnings-container">`
- Open Network tab (F12) and check `/observation/latest` response includes warnings array

### Panel overlap still happening
- Hard refresh the page (Ctrl+Shift+R)
- Clear browser cache for localhost:5500
- Check that styles.css has the fixed positioning rules

### Mirror view not working
- Hard refresh (Ctrl+Shift+R) - browser may have cached old CSS
- Check F12 → Elements and look for `transform: scaleX(-1)` on `#candidate-video`
- Try different browser if issue persists

### Performance slow
- Check frame rate: Open Network tab (F12), filter by `add_video_frame` requests
- Should see requests every ~167ms (6 FPS)
- If slower, check backend CPU usage
