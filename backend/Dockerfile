# ── Stage 1: Build Frontend ───────────────────────────────────────────────────
# Use slim-bookworm instead of alpine to ensure native tailwind compatibility
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Copy dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy source
COPY frontend/ ./

# Increase node memory for Vite build (Render free tier limit is 512MB)
ENV NODE_OPTIONS="--max-old-space-size=450"
RUN npm run build

# ── Stage 2: Backend Runtime ──────────────────────────────────────────────────
FROM python:3.11-slim-bookworm AS backend-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy the build result from frontend stage into /app/static/
# Vite builds to 'dist' by default
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# VERIFICATION: Fail the build if index.html is missing
RUN ls -la /app/static/index.html

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
