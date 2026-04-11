import os
import librosa
from model.predictor import load_model, predict

# Load model
load_model()

# Pick one file automatically
base = "data/train_audio"
sample_path = None

for folder in os.listdir(base):
    folder_path = os.path.join(base, folder)
    if os.path.isdir(folder_path):
        files = os.listdir(folder_path)
        if files:
            sample_path = os.path.join(folder_path, files[0])
            break

print("Using:", sample_path)

# Load audio
y, sr = librosa.load(sample_path, sr=None)

# Take 5 sec chunk
chunk = y[:5 * sr]

# Predict
species, confidence = predict(chunk, sr)

print("Species:", species)
print("Confidence:", confidence)