from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import numpy as np
import soundfile as sf
import sys

sys.path.append(str((Path(__file__).parent.parent / ".." / "unophysics").resolve()))
from unophysics._ladc import EARS

app = FastAPI()

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"


@app.get("/files")
def list_files():
    files = [
        f.name
        for f in DATA_DIR.glob("*")
        if f.suffix.lower()
        in {".wav", ".flac", ".aiff", ".aif", ".ogg", ".190", ".010", ".dat", ".bin"}
    ]
    return {"files": files}


@app.get("/file/{filename}")
def load_file(filename: str):
    file_path = DATA_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        ext = file_path.suffix.lower()
        if ext in {".190", ".010", ".dat", ".bin"}:
            # Use unophysics loader
            ears = EARS(str(file_path))
            data = np.array(ears.data, dtype=np.float32)
            samplerate = getattr(ears, "fs", 192000)
            duration = len(data) / samplerate
        else:
            data, samplerate = sf.read(str(file_path))
            duration = len(data) / samplerate
            if len(data.shape) > 1:
                data = data[:, 0]
        # Downsample for plotting (max 5000 points)
        max_points = 5000
        if len(data) > max_points:
            step = len(data) // max_points
            data = data[: step * max_points]
            data = data.reshape(-1, step).mean(axis=1)
        return {
            "filename": filename,
            "samplerate": samplerate,
            "duration": duration,
            "waveform": data.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read audio: {e}")
