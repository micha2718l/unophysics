# Audino: Modern Audio Exploration & Cleaning Web App

## Overview
Audino is a web-based tool for exploring, cleaning, and processing audio files. It features:
- Modern React (TypeScript) frontend with Material UI and Plotly.js for waveform visualization
- FastAPI Python backend for audio file I/O, cleaning, and extensible processing
- Audio playback, scrubbing, and interactive parameter controls

## Project Structure
- `frontend/` — React app (UI, waveform, playback)
- `backend/` — FastAPI app (API, audio processing)

## Getting Started

### Prerequisites
- Node.js (for frontend)
- Python 3.9+ (for backend)

### Setup

#### Backend
```sh
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn numpy soundfile
# (Add your cleaning/processing dependencies as needed)
uvicorn main:app --reload
```

#### Frontend
```sh
cd frontend
npm install
npm start
```

### Usage
- Open the frontend in your browser (default: http://localhost:3000)
- The backend runs on http://localhost:8000

## Extending
- Add new cleaning/processing functions in the backend (Python)
- Add new UI controls in the frontend (React)

---
