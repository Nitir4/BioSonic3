import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from main import run_pipeline
from model.predictor import load_model

# ── Allowed frontend origins ───────────────────────────────────────────────────
# Set ALLOWED_ORIGINS env var on Render to your Vercel URL, e.g.:
#   https://biosonic.vercel.app
# Comma-separate multiple values if needed.
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",")]


# ── Lifespan: load model once at startup ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BioSonic API",
    description="Wildlife audio classification backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict_audio(file: UploadFile = File(...)):
    """
    Accept any audio file supported by librosa (.ogg, .wav, .mp3, .flac …)
    and return:
      species   – predicted wildlife species
      confidence – model confidence [0, 1]
      rai       – Relative Abundance Index (detections / minute)
      zones     – { A: int, B: int, C: int } occurrence counts per zone
      movement  – human-readable movement pattern string
    """
    # Preserve the original extension so librosa can pick the right decoder
    suffix = os.path.splitext(file.filename or "audio")[1] or ".ogg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name

    try:
        result = run_pipeline(temp_path)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Audio processing failed: {exc}")
    finally:
        os.unlink(temp_path)

    return result