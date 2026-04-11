import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from main import run_pipeline
from model.predictor import load_model

# ── Lifespan: load model once at startup ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BioSonic API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes (Must come BEFORE static/catch-all) ─────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict_audio(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "audio")[1] or ".ogg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name
    try:
        result = run_pipeline(temp_path)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        os.unlink(temp_path)
    return result

# ── Frontend Logic ────────────────────────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# 1. Serve individual files in the root static folder (favicon, icons, etc.)
# But do NOT mount it to '/' as it intercepts routes. 
# We'll handle them via a specific check or use a subpath.

@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found. Please ensure 'npm run build' was successful."}

# Serve the /assets/ folder for JS/CSS
assets_path = os.path.join(STATIC_DIR, "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# Catch-all for React router and other root-level static files
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Check if the file exists in static folder (e.g. /favicon.svg)
    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise, return index.html for React routing
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Not Found")
