# Quick Start Guide - AI Interviewer

## 🚀 Get Started in 5 Minutes

### Step 1: Get Your Free Gemini API Key
1. Go to [https://ai.google.dev](https://ai.google.dev)
2. Click "Get API Key" → "Create API key in new project"
3. Copy your API key

### Step 2: Setup Backend

```powershell
# Navigate to project
cd d:\AI_interviewer\ai-interviewer

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file with your API key
@"
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
"@ | Out-File -FilePath .env -Encoding utf8

# Start the backend server
python -m uvicorn backend.main:app --reload --port 8000
```

### Step 3: Setup Frontend

Open a **new terminal** (keep backend running):

```powershell
# Navigate to frontend folder
cd d:\AI_interviewer\ai-interviewer\frontend

# Start HTTP server
python -m http.server 5500
```

### Step 4: Open in Browser

Go to: [http://localhost:5500](http://localhost:5500)

**Recommended browsers:**
- Chrome (best support)
- Edge (best support)
- Safari (good support)
- Firefox (limited - no voice input)

### Step 5: Start Interview

1. Click **"Start Interview"** button
2. Avatar will greet you
3. **Answer questions:**
   - **Type**: Use the text input field
   - **Speak**: Click the 🎤 microphone button and speak
4. Interview progresses through technical, behavioral, and stress testing phases
5. Avatar thanks you at the end

---

## 🎙️ Using Voice Input

1. Click the 🎤 button
2. Button turns red and pulses - you're being recorded
3. Speak your answer clearly
4. Click 🎤 again or wait for recognition to finish
5. Your speech appears in the text field
6. Click "Send" or press Enter

**First time?** Your browser will ask for microphone permission - click "Allow"

---

## 🎨 Avatar Features

- **Blinking eyes** - Blinks automatically every 3-7 seconds
- **Talking mouth** - Moves when speaking
- **Facial expressions** - Changes color based on interview state:
  - Warm tone = friendly, listening
  - Darker tone = serious, evaluating
  - Red tone = stress testing
  - Light tone = happy, greeting

---

## ❓ Troubleshooting

### Backend won't start
```powershell
# Make sure you're in the virtual environment
.\.venv\Scripts\Activate.ps1

# Verify dependencies are installed
pip list

# Check if port 8000 is free
netstat -ano | findstr :8000
```

### Frontend won't load
```powershell
# Make sure backend is running first
# Check browser console (F12) for errors
# Try a different port if 5500 is busy:
python -m http.server 5501
```

### Voice input not working
- ✅ Use Chrome, Edge, or Safari
- ❌ Firefox doesn't support speech recognition
- Check microphone permissions in browser settings
- Ensure you're using HTTP or HTTPS (not file://)

### Avatar doesn't appear
- Check browser console (F12) for errors
- Verify Three.js CDN is loading
- Try refreshing the page
- Clear browser cache

### Gemini API quota exceeded
- Free tier has rate limits
- Wait 24 hours for reset (UTC midnight)
- Or get a new API key

---

## 📊 What to Expect

**Interview Stages:**
1. **GREETING** - Warm welcome
2. **WARM_UP** - Background questions
3. **TECHNICAL** - Technical skills assessment
4. **PROBLEM_SOLVING** - Algorithm and design questions
5. **BEHAVIORAL** - Soft skills and experience
6. **STRESS** - Handling pressure
7. **CLOSURE** - Thank you and next steps

**Duration:** Typically 15-20 questions depending on your answers

**Realistic Experience:** The AI interviewer responds naturally and adapts to your answers, just like a real interview.

---

## 🎯 Pro Tips

1. **Speak clearly** - The speech recognition works best with clear, moderate-paced speech
2. **Be concise** - Aim for 1-2 minute answers
3. **Use examples** - The AI appreciates specific examples from your experience
4. **Ask for clarification** - If a question is unclear, just ask
5. **Take your time** - No rush, think through your answers
6. **Test your setup** - Do a quick test with typing before using voice input

---

## 💡 Features You'll Love

✅ Realistic 3D avatar with blinking eyes and talking mouth
✅ Voice input - speak your answers naturally
✅ Voice output - hear questions spoken to you
✅ Professional interview flow
✅ Real-time feedback through facial expressions
✅ Smooth, production-quality experience

---

## 🆘 Need Help?

Check the full README.md for:
- Detailed architecture
- Browser compatibility table
- Complete troubleshooting guide
- API documentation
- Testing procedures

Or check CHANGELOG.md for:
- Complete feature list
- Implementation details
- Technical specifications

---

**Ready? Let's ace that interview! 🚀**
