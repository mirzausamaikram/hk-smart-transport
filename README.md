# 🚇 HK Smart Transport

A comprehensive Hong Kong public transportation app providing real-time route planning, nearby station search, and intelligent itinerary generation for MTR, buses, ferries, and more.

## ✨ Features

- 🗺️ **Interactive Maps**: Leaflet-powered maps showing stations, routes, and points of interest
- 🔍 **Smart Search**: Geocoding and location search with autocomplete
- 🚉 **Nearby Stations**: Find MTR stations, bus stops, and ferry piers near any location
- 🛤️ **Route Planning**: Multi-modal journey planning across different transport types
- 🤖 **AI Itinerary**: Intelligent trip planning powered by AI
- 📍 **POI Integration**: Discover attractions, restaurants, and landmarks
- 🚌 **Multi-Transport**: Support for MTR, CityBus, Star Ferry, and more

## 🏗️ Architecture

### Backend (FastAPI)
- Python-based REST API
- Real-time transport data integration
- Geocoding and spatial queries
- OpenStreetMap integration
- AI-powered route optimization

### Frontend (SvelteKit)
- Modern, reactive UI with Svelte 5
- TypeScript for type safety
- Leaflet for interactive mapping
- Responsive design

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or pnpm

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mirzausamaikram/hk-smart-transport.git
cd hk-smart-transport
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

**If you encounter pandas installation errors:**
```bash
# Use the minimal requirements without pandas/numpy
pip install -r requirements-minimal.txt
```

Note: Pandas is only needed for advanced pedestrian network routing. The app works perfectly without it.

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Variables**
Create a `.env` file in the root directory:
```env
# Add your API keys and configuration here
```

### Running the Application

**Option 1: Using the startup script (Windows)**
```powershell
.\start.ps1
```

**Option 2: Manual start**

Terminal 1 - Backend:
```bash
cd backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

The app will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
hk-smart-transport/
├── backend/              # FastAPI backend
│   ├── routers/         # API route handlers
│   ├── data/            # Static data and caches
│   └── *.py             # Utility scripts
├── frontend/            # SvelteKit frontend
│   ├── src/
│   │   ├── lib/        # Components and utilities
│   │   └── routes/     # Page components
│   └── static/         # Static assets
├── data-scripts/        # Data processing scripts
└── database/           # Database schemas/migrations
```

## 🛠️ Tech Stack

**Frontend:**
- SvelteKit 2.x
- TypeScript
- Leaflet & Leaflet.markercluster
- Axios

**Backend:**
- FastAPI
- Python 3.x
- OpenStreetMap (Overpass API)
- Various HK transport APIs

## 🐛 Troubleshooting

### Backend Installation Issues

**Problem: "metadata generation for pandas failed"**

This is a common issue with pandas on some systems. Solutions:

1. **Use minimal requirements (Recommended)**
   ```bash
   cd backend
   pip install -r requirements-minimal.txt
   ```

2. **Install pandas separately with prebuilt wheels**
   ```bash
   pip install --upgrade pip
   pip install pandas --only-binary :all:
   ```

3. **Use Python 3.11 or 3.12** (best compatibility)
   ```bash
   python --version  # Check your version
   ```

4. **On Windows, install Visual C++ Build Tools** (if needed)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Problem: "No module named 'uvicorn'"**
```bash
pip install uvicorn[standard]
```

**Problem: "Port 8000 already in use"**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Frontend Installation Issues

**Problem: "npm install fails"**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem: "Module not found" errors**
```bash
cd frontend
npm install
npm run dev
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Hong Kong open transport data providers
- OpenStreetMap contributors
- Svelte and FastAPI communities

---

Made with ❤️ for Hong Kong travelers
