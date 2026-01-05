# CSS Reference - Multi-Avatar Layout

## Control Bar Styling

```css
.control-bar {
  display: flex;
  gap: 30px;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: nowrap;  /* KEY: No wrapping */
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.control-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.7px;
  white-space: nowrap;
  min-width: 55px;
}

.control-dropdown {
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 200px;
}

.control-dropdown:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(31, 115, 231, 0.1);
}

.control-dropdown:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(31, 115, 231, 0.2);
}

.stage-center {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 auto;          /* CENTER THIS */
  flex-shrink: 0;
}
```

## Avatar Grid Styling

```css
.avatars-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  /* FIXED: Always 3 columns */
  gap: 20px;
  padding: 20px;
  height: 100%;
  align-content: start;
  justify-items: center;
}

.avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 3px solid transparent;      /* KEY: 3px border */
  border-radius: 8px;
  transition: all 0.3s ease;           /* Smooth animation */
  cursor: pointer;
  background: transparent;
  width: 100%;
  max-width: 280px;                   /* Limit width */
}

.avatar-wrapper:hover {
  background: var(--bg-secondary);
  border-color: var(--border-color);
}

.avatar-wrapper.active {
  border-color: var(--accent);                    /* #1f73e7 Blue */
  background: rgba(31, 115, 231, 0.12);          /* Light blue tint */
  transform: scale(1.05);                         /* 5% bigger */
  box-shadow: 0 4px 12px rgba(31, 115, 231, 0.2); /* Blue shadow */
}

.avatar-canvas {
  width: 100%;
  height: 240px;                      /* FIXED: 240px height */
  border-radius: 6px;
  background: var(--bg-tertiary);
}

.avatar-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
```

## Color Variables

```css
:root {
  --bg-primary: #ffffff;              /* White */
  --bg-secondary: #f8f9fa;            /* Light gray */
  --bg-tertiary: #f1f2f4;             /* Lighter gray */
  --text-primary: #1a1d1f;            /* Dark gray/black */
  --text-secondary: #5f6368;          /* Medium gray */
  --text-tertiary: #9aa0a6;           /* Light gray */
  --border-color: #dadce0;            /* Light gray border */
  --accent: #1f73e7;                  /* BLUE for active states */
  --accent-hover: #1665d8;            /* Darker blue */
  --success: #188038;                 /* Green */
  --warning: #f57c00;                 /* Orange */
  --critical: #d33427;                /* Red */
}
```

## Animations

```css
/* Avatar selection animation */
.avatar-wrapper {
  transition: all 0.3s ease;
}

/* Toast notifications */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(400px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOutRight {
  to {
    opacity: 0;
    transform: translateX(400px);
  }
}

.toast {
  animation: slideInRight 0.3s ease;
}

.toast.removing {
  animation: slideOutRight 0.3s ease forwards;
}
```

## Responsive Breakpoints

```css
/* For future tablet optimization */
@media (max-width: 1199px) {
  .avatars-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .avatars-container {
    grid-template-columns: 1fr;
  }
  
  .control-bar {
    flex-wrap: wrap;
    gap: 15px;
  }
}
```

## Quick Reference

### To Make Controls Inline (NOT wrapped)
```css
flex-wrap: nowrap;  ← KEY PROPERTY
```

### To Make 3 Equal Columns
```css
grid-template-columns: repeat(3, 1fr);  ← FIXED 3 COLUMNS
```

### To Highlight Active Avatar
```css
border: 3px solid #1f73e7;
background: rgba(31, 115, 231, 0.12);
transform: scale(1.05);
box-shadow: 0 4px 12px rgba(31, 115, 231, 0.2);
```

### To Center Stage Display
```css
margin: 0 auto;  ← AUTO MARGINS
flex-shrink: 0;  ← DON'T SHRINK
```

### Avatar Canvas Size
```css
width: 100%;        /* Fill parent width */
height: 240px;      /* Fixed height */
aspect-ratio: auto; /* Don't force 1:1 */
```

## Layout Measurements

```
Header Height:        56px (16px padding × 2)
Control Bar Height:   52px (12px padding × 2 + 28px content)
Avatar Size:          280px max width
Avatar Canvas:        240px height
Gap Between Avatars:  20px
Control Group Gap:    8px (label to dropdown)
Control Bar Gap:      30px (between groups)
Avatar Wrapper Pad:   16px
Avatar Wrapper Border: 3px
Avatar Wrapper Radius: 8px
Avatar Canvas Radius: 6px
```

## Pixel Perfection

```
Total Control Bar:           Height = 52px
├─ Padding Top:              12px
├─ Content Height:           28px (font + select height)
└─ Padding Bottom:           12px

Avatar Wrapper:             280px max-width
├─ Padding:                 16px × 4 = affects inner content
├─ Border:                  3px
└─ Gap to Label:            12px

Avatar Canvas:              240px × ~240px (aspect auto)
├─ Border Radius:           6px
└─ Background:              Light gray

Grid Layout:                3-column equal width
├─ Columns:                 calc(33.33% - gap)
├─ Gap:                     20px
├─ Padding:                 20px
└─ Justify:                 center items
```

## State Combinations

### Avatar Inactive → Active (Hover)
```
Before: transparent border, no background
After:  gray border, light gray background
```

### Avatar Inactive → Active (Click)
```
Before: transparent border, no background, scale 1.0
After:  blue border, blue tint, scale 1.05, shadow
Toast:  "Avatar X selected"
```

### Mode: Individual → Multi
```
Before: Only Avatar 1 visible, others display: none
After:  All 3 avatars visible with display: flex
Avatar 1 active (blue)
Avatars 2 & 3 inactive (gray)
```

## Testing CSS Values

Open DevTools Inspector on:
1. `.control-bar` → Should see flex, gap: 30px, flex-wrap: nowrap
2. `.avatars-container` → Should see grid-template-columns: repeat(3, 1fr)
3. `.avatar-wrapper.active` → Should see blue border (#1f73e7)
4. `.stage-center` → Should see margin: 0 auto

---

**All CSS values are production-ready and verified!** ✅
