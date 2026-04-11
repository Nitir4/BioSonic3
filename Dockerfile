# ── Stage 1: Build React Frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Copy dependencies first for caching
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
ENV NODE_OPTIONS="--max-old-space-size=450"
RUN npm run build

# ── Stage 2: Final Unified Image (Python + Static Frontend) ──────────────────
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies for audio and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./

# Copy the built frontend from Stage 1 into the backend's static directory
# We put it in 'static' because backend/api.py is configured to serve from there
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# Safety check: Verify the frontend build exists in the final image
RUN ls -la /app/static/index.html

# Run the FastAPI server which now handles both API and Frontend
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}
