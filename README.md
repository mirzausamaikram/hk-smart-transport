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
