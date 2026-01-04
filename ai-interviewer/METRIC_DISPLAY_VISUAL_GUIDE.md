# Metric Display System - Visual Guide

## Overview

The AI Interviewer now displays 4 key performance metrics in a professional 2×2 grid with progress bars.

---

## Metric Box Structure

```
┌─────────────────────────────────────┐
│  METRIC NAME (uppercase label)      │  <- .metric-name
│  9        /10                       │  <- .metric-value + .metric-max
│  █████████░░░░░░░░░░░░░░░░░░░░░░░░  │  <- .metric-bar + .metric-bar-fill
└─────────────────────────────────────┘
   Padding: 12px
   Background: Light Gray (#f1f2f4)
   Border: 1px solid (#dadce0)
   Border Radius: 6px
   Box Shadow: 0 1px 2px rgba(0,0,0,0.05)
```

---

## Grid Layout

### Desktop View (≥1024px)

```
┌────────────────────────────────────────────────┐
│           PERFORMANCE METRICS                  │
├──────────────────────┬──────────────────────────┤
│  Eye Contact         │  Focus                   │
│  8          /10      │  9          /10          │
│  ████████░░░░░░░    │  █████████░░░░░░░░░░░  │
├──────────────────────┼──────────────────────────┤
│  Stress              │  Voice                   │
│  medium              │  7          /10          │
│  █████░░░░░░░░░░░   │  ███████░░░░░░░░░░░░  │
└──────────────────────┴──────────────────────────┘

Dimensions:
  Grid: 2 columns × 2 rows
  Gap: 8px between items
  Each metric: ~100px × 90px
```

### Mobile View (<768px)

```
┌──────────────────────┐
│  Eye Contact         │
│  8          /10      │
│  ████████░░░░░░░    │
├──────────────────────┤
│  Focus               │
│  9          /10      │
│  █████████░░░░░░░░  │
├──────────────────────┤
│  Stress              │
│  medium              │
│  █████░░░░░░░░░░░   │
├──────────────────────┤
│  Voice               │
│  7          /10      │
│  ███████░░░░░░░░░░  │
└──────────────────────┘

Dimensions:
  Grid: 1 column × 4 rows
  Gap: 8px between items
  Each metric: Full width
```

---

## Metric Specifications

### 1. Eye Contact
**Purpose**: Measures if candidate is looking at camera

**Score Display**:
- Format: `0-10` (integer)
- Calculation: `Math.round(eye_contact_confidence * 10)`
- Range: 0 = not looking, 10 = perfect eye contact

**Progress Bar**:
- Fill: 0-100%
- Formula: `eye_contact_confidence * 100%`
- Example: confidence 0.85 → 85% bar

**Missing Data**:
- Shows: `—` (em dash)
- Bar: 0%
- Condition: `!face.face_detected`

**Color**:
- Score text: Blue (#1f73e7)
- Bar fill: Blue (#1f73e7)
- Background: Light gray (#f1f2f4)

**Example States**:
```
Good:      8 /10  ████████░░░░░░░░░░░░░░  (80% blue bar)
Medium:    5 /10  █████░░░░░░░░░░░░░░░░░░  (50% blue bar)
Poor:      2 /10  ██░░░░░░░░░░░░░░░░░░░░░  (20% blue bar)
Missing:   —      (no bar, 0% width)
```

---

### 2. Focus
**Purpose**: Measures if candidate is focused and attentive

**Score Display**:
- Format: `3/6/9` (discrete values)
- Logic:
  - 9 = looking at camera
  - 6 = neutral gaze
  - 3 = looking away
- Fixed score (not continuous)

**Progress Bar**:
- Fill: 30% / 60% / 90%
- Formula: `(focusScore / 10) * 100%`
- Visual scale:
  - 3 → 30% (red zone, looking away)
  - 6 → 60% (yellow zone, neutral)
  - 9 → 90% (green zone, focused)

**Missing Data**:
- Shows: `—` (em dash)
- Bar: 0%

**Color**:
- Score text: Blue (#1f73e7)
- Bar fill: Blue (#1f73e7)
- No color coding (only blue accent)

**Example States**:
```
Focused:    9 /10  █████████░░░░░░░░░░░░░  (90% blue bar)
Neutral:    6 /10  ██████░░░░░░░░░░░░░░░░  (60% blue bar)
Distracted: 3 /10  ███░░░░░░░░░░░░░░░░░░░  (30% blue bar)
Missing:    —      (no bar, 0% width)
```

---

### 3. Stress
**Purpose**: Measures stress level from voice analysis

**Score Display**:
- Format: `"high" / "medium" / "low" / "calibrating"`
- Text value (no numeric score)
- String representation of stress state
- Special state: "calibrating" during initialization

**Progress Bar**:
- Fill: 80% / 50% / 20% / 0%
- Mapping:
  - "high" → 80% (8 out of 10)
  - "medium" → 50% (5 out of 10)
  - "low" → 20% (2 out of 10)
  - "calibrating" → 0% or current state

**Missing Data**:
- Shows: Default "low" (assumes calm state)
- Bar: 20%
- Condition: No stress_level data

**Color**:
- Score text: Blue (#1f73e7) - NOT color coded
- Bar fill: Blue (#1f73e7) - Same for all levels
- No red for "high" stress (professional, calm appearance)

**Example States**:
```
High Stress:    high      ████████░░░░░░░░░░░░░░  (80% blue bar)
Medium Stress:  medium    █████░░░░░░░░░░░░░░░░░░  (50% blue bar)
Low Stress:     low       ██░░░░░░░░░░░░░░░░░░░░░  (20% blue bar)
Calibrating:    calibrating (updating...)
```

---

### 4. Voice
**Purpose**: Measures voice confidence and clarity

**Score Display**:
- Format: `0-10` (integer)
- Calculation: `Math.round(voice_confidence * 10)`
- Range: 0 = no voice, 10 = perfect clarity

**Progress Bar**:
- Fill: 0-100%
- Formula: `voice_confidence * 100%`
- Example: confidence 0.72 → 72% bar

**Missing Data**:
- Shows: `—` (em dash)
- Bar: 0%
- Condition: `voice_confidence === null or undefined`

**Color**:
- Score text: Blue (#1f73e7)
- Bar fill: Blue (#1f73e7)
- Background: Light gray (#f1f2f4)

**Example States**:
```
Clear:    8 /10  ████████░░░░░░░░░░░░░░  (80% blue bar)
Moderate: 6 /10  ██████░░░░░░░░░░░░░░░░  (60% blue bar)
Weak:     3 /10  ███░░░░░░░░░░░░░░░░░░░  (30% blue bar)
Missing:  —      (no bar, 0% width)
```

---

## Styling Details

### Metric Container
```css
.metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: #f1f2f4;
  border: 1px solid #dadce0;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
```

### Metric Name (Label)
```css
.metric-name {
  font-size: 11px;
  font-weight: 600;
  color: #5f6368;
  text-transform: uppercase;
  letter-spacing: 0.2px;
}
/* Example: "Eye Contact", "Focus", "Stress", "Voice" */
```

### Metric Value (Score)
```css
.metric-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.metric-score {
  font-size: 18px;
  font-weight: 600;
  color: #1f73e7;  /* Professional blue */
}

.metric-max {
  font-size: 12px;
  color: #9aa0a6;
}
/* Example: "8" + "/10" = "8 /10" */
```

### Progress Bar
```css
.metric-bar {
  width: 100%;
  height: 4px;
  background: #dadce0;  /* Light gray background */
  border-radius: 2px;
  overflow: hidden;
}

.metric-bar-fill {
  height: 100%;
  background: #1f73e7;  /* Professional blue fill */
  border-radius: 2px;
  transition: width 0.3s ease;  /* Smooth animation */
}
```

---

## Animation Details

### Bar Fill Animation
```css
transition: width 0.3s ease;
```

**Behavior**:
- Duration: 300 milliseconds
- Easing: `ease` (slow-fast-slow)
- Property: Only width changes
- Frequency: Updates every 250ms from backend (observation polling)

**Visual Effect**:
```
Initial State:
  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (0%)

Transition (over 300ms):
  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (intermediate)
  ████████░░░░░░░░░░░░░░░░░░░░░░░░  (intermediate)
  ████████████░░░░░░░░░░░░░░░░░░░░  (intermediate)

Final State:
  ████████████████░░░░░░░░░░░░░░░░  (50%)
```

**Update Frequency**:
- Backend poll: Every 250ms (4 FPS)
- Animation duration: 300ms
- Result: Smooth, continuous bar fills

---

## JavaScript Implementation

### Element IDs
```javascript
// Score display
document.getElementById("metric-eye-contact")    // Text: "8" or "—"
document.getElementById("metric-focus")         // Text: "9" or "—"
document.getElementById("metric-stress")        // Text: "high" or "—"
document.getElementById("metric-voice")         // Text: "7" or "—"

// Progress bars
document.getElementById("metric-eye-contact-bar")  // Style: width 0-100%
document.getElementById("metric-focus-bar")        // Style: width 0-100%
document.getElementById("metric-stress-bar")       // Style: width 0-100%
document.getElementById("metric-voice-bar")        // Style: width 0-100%
```

### Update Logic
```javascript
// Eye Contact
const eyeContactBar = document.getElementById("metric-eye-contact-bar");
eyeContactBar.style.width = `${confidence * 100}%`;  // 0-100%

// Focus
const focusBar = document.getElementById("metric-focus-bar");
focusBar.style.width = `${(focusScore / 10) * 100}%`;  // 30%, 60%, or 90%

// Stress
const stressBar = document.getElementById("metric-stress-bar");
const stressNumeric = stress === "high" ? 8 : stress === "medium" ? 5 : 2;
stressBar.style.width = `${(stressNumeric / 10) * 100}%`;  // 20%, 50%, or 80%

// Voice
const voiceBar = document.getElementById("metric-voice-bar");
voiceBar.style.width = `${voice * 100}%`;  // 0-100%
```

---

## User Experience

### Visual Feedback
- **Real-time**: Updates every 250ms from backend
- **Smooth**: 300ms animation on bar fills
- **Professional**: Blue accent color (#1f73e7)
- **Clear**: No color coding, consistent styling

### Information Hierarchy
1. **Metric Name** (top, small, gray): What is measured
2. **Score** (middle, large, blue): Current value
3. **Progress Bar** (bottom, blue fill): Visual representation

### Missing Data Handling
- Shows `—` (em dash) instead of 0
- Indicates "no data available" vs "low score"
- Bar width: 0% (empty)
- Maintains layout integrity

---

## Responsive Behavior

### Desktop (≥1024px)
```
2 columns × 2 rows grid
┌────┬────┐
│ 1  │ 2  │
├────┼────┤
│ 3  │ 4  │
└────┴────┘
```

### Tablet (768-1023px)
```
2 columns × 2 rows grid (may wrap based on width)
Or 1 column × 4 rows if insufficient width
```

### Mobile (<768px)
```
1 column × 4 rows layout
┌────┐
│ 1  │
├────┤
│ 2  │
├────┤
│ 3  │
├────┤
│ 4  │
└────┘
```

---

## Color Consistency

### Color Palette
- **Blue Accent (#1f73e7)**:
  - Metric score text
  - Progress bar fill
  - Button colors
  - Active states
  - Links

- **Gray Backgrounds (#f1f2f4)**:
  - Metric container
  - Secondary panels
  - Hover states
  - Audio visualizer

- **Dark Text (#1a1d1f)**:
  - Labels
  - Headers
  - Primary text

- **Light Text (#9aa0a6)**:
  - Secondary labels
  - "/10" indicators
  - Hints

---

## Testing Checklist

### Visual Testing
- [ ] All 4 metrics visible in 2×2 grid
- [ ] Metrics display correct values
- [ ] Progress bars animate smoothly
- [ ] Colors match specification (#1f73e7 blue)
- [ ] Layout responsive at 1920px, 1024px, 768px, 375px

### Functional Testing
- [ ] Eye contact updates with face detection
- [ ] Focus updates based on gaze direction
- [ ] Stress displays "high"/"medium"/"low"
- [ ] Voice displays 0-10 score
- [ ] Missing data shows "—"
- [ ] Bars animate every 250ms

### Edge Cases
- [ ] No face detected → "—" and 0% bar
- [ ] Missing voice data → "—" and 0% bar
- [ ] Stress "calibrating" → "calibrating" text
- [ ] All metrics missing → All show "—"
- [ ] All metrics perfect → All show max values

---

## Summary

The metric display system provides:
- ✅ Clear, professional visual representation
- ✅ Real-time updates with smooth animations
- ✅ Responsive design on all devices
- ✅ Consistent blue accent color
- ✅ Missing data handled gracefully
- ✅ Professional enterprise appearance

All metrics work together to give the candidate immediate feedback on their interview performance.
