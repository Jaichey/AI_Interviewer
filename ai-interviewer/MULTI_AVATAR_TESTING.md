# UI Testing Guide - Multi-Avatar Implementation

## Testing Checklist

### 1. Initial Page Load
- [ ] Page loads without errors
- [ ] Control bar visible below header
- [ ] All 3 avatars visible in avatar panel
- [ ] Subject, Mode, Company dropdowns populated
- [ ] Stage label shows "WARM_UP"
- [ ] Buttons visible: Continuous, Start Interview, End Interview
- [ ] No console errors

### 2. Control Bar Functionality

#### Subject Dropdown
- [ ] Click Subject dropdown
- [ ] Verify all 8 options visible: DAA, OS, CN, SE, WEB, DBMS, OOPS, System Design
- [ ] Select "DAA"
- [ ] Toast notification appears: "Subject changed to DAA"
- [ ] Try other subjects
- [ ] Toast shows each selection

#### Mode Dropdown
- [ ] Click Mode dropdown
- [ ] Verify 2 options: Individual Interviewer, Multi Interviewer (3 Avatars)
- [ ] Default should be "Individual Interviewer"
- [ ] Select "Multi Interviewer (3 Avatars)"
- [ ] Toast shows: "Multi-avatar mode selected - 3 avatars will be active"
- [ ] All 3 avatars remain visible
- [ ] Switch back to "Individual Interviewer"
- [ ] Toast shows: "Individual mode selected"
- [ ] Only Avatar 1 remains visible (2 and 3 hidden)
- [ ] Switch back to "Multi Interviewer"
- [ ] Avatars 2 and 3 reappear

#### Company Dropdown
- [ ] Click Company dropdown
- [ ] Verify all 7 companies listed
- [ ] Select "Google"
- [ ] Toast shows: "Interview style: analytical - Emphasis: problem-solving and algorithm optimization"
- [ ] Try other companies (Amazon, Meta, etc.)
- [ ] Different toast messages for each company

### 3. Avatar Display and Styling

#### Initial State (Individual Mode)
- [ ] Only Avatar 1 visible
- [ ] Avatar has border and canvas visible
- [ ] Avatar label shows "AVATAR 1"
- [ ] Canvas displays Three.js avatar (if model loads)
- [ ] Avatar state shows: "neutral_listening"
- [ ] Status shows: "disconnected"

#### Switch to Multi Mode
- [ ] Click Mode dropdown → select "Multi Interviewer"
- [ ] Avatar 2 appears next to Avatar 1
- [ ] Avatar 3 appears next to Avatar 2
- [ ] All 3 in 3-column grid layout
- [ ] Avatar 1 has blue border (active)
- [ ] Avatars 2 and 3 have gray/transparent border

#### Avatar Selection
- [ ] Click on Avatar 2 in multi-mode
- [ ] Avatar 2 gets blue border and scales up slightly
- [ ] Avatar 1 border becomes gray
- [ ] Toast notification: "Avatar 2 selected"
- [ ] Click Avatar 3
- [ ] Avatar 3 becomes active (blue)
- [ ] Avatar 2 becomes inactive (gray)
- [ ] Toast notification: "Avatar 3 selected"
- [ ] Click Avatar 1
- [ ] Avatar 1 active again
- [ ] Toast notification: "Avatar 1 selected"

## Expected Results

### On Load
```
✓ Header visible with brand and 3 buttons
✓ Control bar with 4 dropdowns (Subject, Mode, Stage, Company)
✓ Avatar panel showing 3 avatars in 3-column grid
✓ All avatars rendering (empty if model not loaded)
✓ Avatar 1 highlighted (blue border)
✓ Avatars 2 & 3 with gray border
✓ Right panel with camera and messages
```

### After Starting Interview
```
✓ Consent modal appears
✓ Accept consent → Camera starts
✓ WebSocket connects
✓ Interview begins
✓ Avatar receives questions for selected subject + company difficulty
```

---
