FROM python:3.11-slim

# System libs for librosa/soundfile, ffmpeg for audio decoding, opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code + model weights
COPY . .

# Model weights are expected at:
#   model/weights/regnety008.pth
#   model/weights/class_names.pkl
# These should be present in the build context (committed to git, or downloaded in CI)

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
