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
    # Log startup for debugging
    print("INFO: Starting BioSonic API...")
    load_model()
    yield
    print("INFO: Shutting down BioSonic API...")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BioSonic API",
    lifespan=lifespan,
)

# Extremely permissive CORS for initial deployment troubleshooting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes (Must come BEFORE static/catch-all) ─────────────────────────────
@app.get("/health")
@app.head("/health")
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
        print(f"ERROR: Prediction failed: {exc}")
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        os.unlink(temp_path)
    return result

# ── Frontend Logic ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Serve favicon.ico specifically to avoid 404s in logs
@app.get("/favicon.ico")
async def favicon():
    fav_path = os.path.join(STATIC_DIR, "favicon.svg") # Vite often uses svg
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return HTTPException(status_code=404)

# Support HEAD / for Render health checks
@app.get("/")
@app.head("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend build not found.", "path": index_path}

# Serve the /assets/ folder for JS/CSS
assets_path = os.path.join(STATIC_DIR, "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# Catch-all for React router and other root-level static files
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Not Found")
