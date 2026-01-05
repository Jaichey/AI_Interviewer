# AI Interviewer UI - Layout Comparison

## Before vs After

### BEFORE (Previous Layout)
```
┌──────────────────────────────────────────────────────────────────────┐
│ AI Interviewer          [WARM_UP]     Continuous Start End         │
└──────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│ Subject    Mode    Company  (All Dropdowns in Single Bar)           │
└──────────────────────────────────────────────────────────────────────┘
┌───────────────────────────────────┬──────────────────────────────────┐
│                                    │                                  │
│          AVATAR PANEL              │      CAMERA PANEL               │
│          (Single Avatar)           │      (Candidate Video)          │
│                                    │                                  │
├───────────────────────────────────┼──────────────────────────────────┤
│  Avatar: neutral_listening         │   MESSAGE PANEL                 │
│  Status: disconnected              │   (Conversation)                │
└───────────────────────────────────┴──────────────────────────────────┘
```

### AFTER (Fixed Layout - Matches Wireframe)
```
┌──────────────────────────────────────────────────────────────────────┐
│ AI Interviewer                          Continuous Start End        │
└──────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│ SUBJECT          MODE              WARM_UP          COMPANY          │
│  [▼]          [▼]                                      [▼]           │
└──────────────────────────────────────────────────────────────────────┘
┌───────────────────────────────────┬──────────────────────────────────┐
│                                    │                                  │
│      AVATAR PANEL (70%)            │    CAMERA PANEL (30%)           │
│    ┌──────────┬──────────┬──────┐  │  ┌──────────────────────────┐   │
│    │ AVATAR 1 │ AVATAR 2 │ AVA  │  │  │  CANDIDATE CAMERA       │   │
│    │ (Canvas) │ (Canvas) │ 3    │  │  │  (Video Feed)           │   │
│    │          │          │      │  │  │                          │   │
│    │ Active   │ Inactive │ Ina  │  │  │                          │   │
│    │ (Blue)   │ (Gray)   │ (G)  │  │  │                          │   │
│    └──────────┴──────────┴──────┘  │  │                          │   │
│                                    │  └──────────────────────────┘   │
│    Avatar: neutral_listening       │  MESSAGE PANEL                 │
│    Status: disconnected            │  (Conversation History)         │
│                                    │  [Input Box] [Mic] [Send]      │
└───────────────────────────────────┴──────────────────────────────────┘
```

## Key Layout Changes

### 1. Header Restructuring
**BEFORE:**
- Header had 3 sections: Left (Brand) | Center (Stage) | Right (Buttons)
- All controls in header

**AFTER:**
- Header: Left (Brand) | Right (Buttons ONLY)
- New Control Bar below header: Subject | Mode | Stage | Company
- Clean separation of concerns

### 2. Control Bar Layout
**BEFORE:**
- Wrapped layout, items could break to multiple lines
- Large label text "Subject", "Mode", "Company"
- Variable dropdown widths

**AFTER:**
- Single-line flex layout (no wrapping)
- Compact uppercase labels: "SUBJECT", "MODE", "COMPANY"
- Stage centered in middle
- Consistent spacing: 30px gaps between groups
- Fixed dropdown widths: 200px

### 3. Avatar Panel - Multi-Avatar Grid
**BEFORE:**
- Single avatar displayed
- Auto-fit grid: `repeat(auto-fit, minmax(200px, 1fr))`
- Only 1 avatar ever visible

**AFTER:**
- Always 3 avatars (all initialized on page load)
- Fixed 3-column grid: `repeat(3, 1fr)`
- All 3 visible simultaneously in multi-mode
- Only first visible in individual-mode (hidden but still running)
- Active avatar highlighted with:
  - Blue border (3px width)
  - Blue background tint
  - Scale-up animation (1.05x)
  - Drop shadow

### 4. Avatar Wrapper Styling
**BEFORE:**
- Smaller canvas: aspect-ratio 1:1
- Transparent background
- Small borders

**AFTER:**
- Fixed height: 240px
- Larger, more prominent display
- Visible borders and background
- Smooth hover effects
- Active state clearly visible

## CSS Measurements

### Control Bar
```css
.control-bar {
  padding: 12px 24px;      /* Compact vertical, generous horizontal */
  gap: 30px;               /* Space between groups */
}

.control-group {
  gap: 8px;                /* Space between label and dropdown */
}

.control-dropdown {
  padding: 6px 10px;       /* Smaller padding */
  min-width: 200px;        /* Fixed minimum width */
  font-size: 12px;         /* Smaller font */
}

.stage-center {
  margin: 0 auto;          /* Auto margins for centering */
  flex-shrink: 0;          /* Don't shrink when space is tight */
}
```

### Avatar Grid
```css
.avatars-container {
  grid-template-columns: repeat(3, 1fr);  /* Exactly 3 equal columns */
  gap: 20px;                               /* Generous spacing */
  justify-items: center;                   /* Center items horizontally */
}

.avatar-wrapper {
  max-width: 280px;                       /* Max width for readability */
  border: 3px solid transparent;          /* Thicker border for visibility */
  transition: all 0.3s ease;              /* Smooth animations */
}

.avatar-wrapper.active {
  border-color: var(--accent);            /* Blue border */
  background: rgba(31, 115, 231, 0.12);   /* Light blue background */
  transform: scale(1.05);                 /* 5% scale-up */
  box-shadow: 0 4px 12px rgba(...);       /* Depth shadow */
}

.avatar-canvas {
  width: 100%;                             /* Fill width */
  height: 240px;                          /* Fixed height */
  border-radius: 6px;                     /* Rounded corners */
  background: var(--bg-tertiary);         /* Light background */
}
```

## Individual vs Multi Mode

### Individual Mode (Default)
```
Control Bar: SUBJECT | MODE=Individual | STAGE | COMPANY
             (All selectable)

Avatar Panel:
┌─────────────────────────────┐
│         AVATAR 1            │
│       (Full Width)          │
│        (Active)             │
│                             │
│      [Canvas - 240px h]     │
│                             │
└─────────────────────────────┘

Behavior:
- Only 1 avatar visible
- Other 2 avatars hidden (CSS display: none)
- Click on avatar: no effect (single mode)
- Dropdown change: Updates single avatar's questions
```

### Multi Interviewer Mode
```
Control Bar: SUBJECT | MODE=Multi | STAGE | COMPANY
             (All selectable)

Avatar Panel:
┌──────────────┬──────────────┬──────────────┐
│   AVATAR 1   │   AVATAR 2   │   AVATAR 3   │
│   (Active)   │ (Inactive)   │ (Inactive)   │
│              │              │              │
│ Blue Border  │ Gray Border  │ Gray Border  │
│ Scale 1.05x  │ Scale 1.0x   │ Scale 1.0x   │
└──────────────┴──────────────┴──────────────┘

Behavior:
- All 3 avatars visible side-by-side
- Avatar 1 active by default (blue border)
- Click Avatar 2/3: Makes it active (show blue border)
- Active avatar gets next question in round-robin
- Each avatar can have different voice/personality
- Toast shows which avatar is selected
```

## Responsive Behavior

### Desktop (1200px+)
- All 3 avatars visible at optimal size
- 280px max-width per avatar
- 20px gaps between avatars
- Control bar single-line layout

### Tablet (768px-1199px)
- 3 avatars might be tight
- Consider 2-column fallback if needed
- Control bar may wrap labels

### Mobile (< 768px)
- Current: Not optimized for mobile
- Future: Could collapse to 1-column avatar view
- Control bar dropdowns might need scroll

## Color Coding

### Active Avatar
- Border: `var(--accent)` = #1f73e7 (Blue)
- Background: `rgba(31, 115, 231, 0.12)` (Light blue tint)
- Shadow: `rgba(31, 115, 231, 0.2)` (Blue shadow)

### Inactive Avatar  
- Border: `transparent`
- Background: `transparent`
- Shadow: `none`

### Hover (Inactive)
- Background: `var(--bg-secondary)` (Light gray)
- Border: `var(--border-color)` (Gray)

## Animation Timings

```css
transition: all 0.3s ease;  /* Avatar selection */

@keyframes slideInRight {
  from { transform: translateX(400px); }
  to { transform: translateX(0); }
}  /* Toast notifications */
```

## Accessibility Features

✅ ARIA labels on dropdowns
✅ Toast notifications with role="alert"
✅ Keyboard navigable (Tab to select)
✅ Color contrast: AA standard
✅ Focus indicators on buttons/dropdowns
✅ Semantic HTML structure

## Summary of Changes

| Aspect | Before | After |
|--------|--------|-------|
| **Header** | 3 sections | 2 sections |
| **Control Bar** | Single-line, wrapped | Single-line, fixed |
| **Stage Display** | In header center | Control bar center |
| **Avatar Count** | 1 visible | 3 always visible (in multi-mode) |
| **Avatar Grid** | Auto-fit flexible | Fixed 3-column |
| **Avatar Canvas Size** | Aspect ratio 1:1 | Fixed 240px height |
| **Active State** | Small highlight | Prominent border + scale + shadow |
| **Dropdowns** | Longer labels | Compact uppercase labels |
| **Layout Spacing** | Variable | Consistent 30px/20px gaps |

---

This layout now matches the provided wireframe exactly and provides a professional interview room experience for multi-avatar mode! 🎉
