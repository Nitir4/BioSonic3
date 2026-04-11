# ── Stage 1: Build Frontend ───────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Build frontend; result goes to /app/frontend/dist
RUN npm run build

# ── Stage 2: Backend Runtime ──────────────────────────────────────────────────
FROM python:3.11-slim-bookworm AS backend-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System libs for librosa/soundfile, ffmpeg for audio decoding, opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cached layer)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy built frontend from Stage 1 to 'static' folder in backend
COPY --from=frontend-builder /app/frontend/dist ./static

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
