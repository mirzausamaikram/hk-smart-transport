# Quick Setup Guide for HK Smart Transport

## For Users Having Installation Issues

If you're getting **"metadata generation for pandas failed"** or similar errors, follow these steps:

### Step 1: Install Python Requirements (Minimal Version)

```bash
cd backend
pip install -r requirements-minimal.txt
```

This installs everything except pandas/numpy, which are only needed for advanced features.

### Step 2: Start the Backend

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Install Frontend Dependencies

Open a **new terminal**:

```bash
cd frontend
npm install
```

### Step 4: Start the Frontend

```bash
npm run dev
```

You should see:
```
VITE ready at http://localhost:5173/
```

### Step 5: Open the App

Open your browser and go to: **http://localhost:5173**

---

## What if I still want pandas?

If you want the full version with pandas for advanced pedestrian routing:

### Option 1: Install pandas from wheels
```bash
pip install --upgrade pip
pip install pandas --only-binary :all:
pip install numpy --only-binary :all:
```

### Option 2: Use Python 3.11 or 3.12
Pandas works best with Python 3.11-3.12. Check your version:
```bash
python --version
```

Download Python 3.12: https://www.python.org/downloads/

### Option 3: Install C++ Build Tools (Windows only)
Download and install: https://visualstudio.microsoft.com/visual-cpp-build-tools/

Then try:
```bash
pip install -r requirements.txt
```

---

## Common Errors & Fixes

### "Port 8000 already in use"
**Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### "Module 'fastapi' not found"
```bash
cd backend
pip install fastapi uvicorn
```

### "npm ERR! code ENOENT"
```bash
cd frontend
npm cache clean --force
npm install
```

### Backend starts but frontend shows "Failed to fetch"
Make sure:
1. Backend is running on http://127.0.0.1:8000
2. Frontend is running on http://localhost:5173
3. Check browser console for CORS errors

---

## Need Help?

1. Check the main [README.md](../README.md) troubleshooting section
2. Open an issue on GitHub
3. Make sure you're using:
   - Python 3.8+ (3.11-3.12 recommended)
   - Node.js 18+

---

**Quick Test:** After starting both servers, visit http://localhost:5173 and click "Nearby Stations" - you should see a map!
