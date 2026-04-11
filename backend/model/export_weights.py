"""
Run this script ONCE on Kaggle to:
  1. Load the RegNetY-008 weights from the model archive
  2. Extract class names from the BirdCLEF training data
  3. Save both as files you download and commit to your repo

Usage (in a Kaggle notebook cell):
  !python export_weights.py

Output files in /kaggle/working/:
  regnety008.pth      — model state dict (~25 MB)
  class_names.pkl     — sorted list of species strings
"""

import os
import tarfile
import glob
import torch
import timm
import joblib

# ── 1. Find and extract the downloaded model archive ──────────────────────────
MODEL_ARCHIVE = "/kaggle/input/regnrty008/pytorch/default/1/model.tar.gz"

# Fallback: search for any tar.gz in the model input folder
if not os.path.isfile(MODEL_ARCHIVE):
    matches = glob.glob("/kaggle/input/regnrty008/**/*.tar.gz", recursive=True)
    if matches:
        MODEL_ARCHIVE = matches[0]
    else:
        # List what's there so we can debug
        for root, dirs, files in os.walk("/kaggle/input/regnrty008"):
            for f in files:
                print(os.path.join(root, f))
        raise FileNotFoundError("Could not find model archive. Check paths printed above.")

print(f"Extracting: {MODEL_ARCHIVE}")
extract_dir = "/kaggle/working/model_extracted"
os.makedirs(extract_dir, exist_ok=True)

with tarfile.open(MODEL_ARCHIVE, "r:gz") as tar:
    tar.extractall(extract_dir)

print("Extracted files:")
for root, _, files in os.walk(extract_dir):
    for f in files:
        print(" ", os.path.join(root, f))

# ── 2. Find the .pth / .pt weight file ────────────────────────────────────────
weight_files = (
    glob.glob(f"{extract_dir}/**/*.pth", recursive=True) +
    glob.glob(f"{extract_dir}/**/*.pt",  recursive=True)
)
if not weight_files:
    raise FileNotFoundError("No .pth or .pt file found inside the archive.")

weight_file = weight_files[0]
print(f"Using weights: {weight_file}")

# ── 3. Load and inspect the checkpoint ────────────────────────────────────────
raw = torch.load(weight_file, map_location="cpu")
print("Checkpoint keys:", list(raw.keys()) if isinstance(raw, dict) else type(raw))

# Pull state dict
if isinstance(raw, dict):
    for key in ("model_state_dict", "model", "state_dict", "net"):
        if key in raw:
            state_dict = raw[key]
            break
    else:
        state_dict = raw  # assume it IS a state dict
else:
    state_dict = raw.state_dict()

# ── 4. Extract class names ─────────────────────────────────────────────────────
# Try to get them from the checkpoint first
class_names = None
if isinstance(raw, dict):
    for key in ("class_names", "classes", "idx_to_class", "label_map"):
        if key in raw:
            val = raw[key]
            if isinstance(val, dict):
                class_names = [val[i] for i in sorted(val.keys())]
            else:
                class_names = list(val)
            print(f"Got {len(class_names)} class names from checkpoint key '{key}'")
            break

# Fallback: read from BirdCLEF train_audio folder
if class_names is None:
    TRAIN_AUDIO = "/kaggle/input/competitions/birdclef-2026/train_audio"
    if os.path.isdir(TRAIN_AUDIO):
        class_names = sorted([
            d for d in os.listdir(TRAIN_AUDIO)
            if os.path.isdir(os.path.join(TRAIN_AUDIO, d))
        ])
        print(f"Got {len(class_names)} class names from train_audio folders")
    else:
        raise RuntimeError(
            "Could not find class names in checkpoint or train_audio. "
            "Add the BirdCLEF competition dataset to this notebook."
        )

print("First 5 classes:", class_names[:5])

# ── 5. Validate: build model and load weights ──────────────────────────────────
num_classes = len(class_names)
net = timm.create_model("regnety_008", pretrained=False, num_classes=num_classes, in_chans=3)

missing, unexpected = net.load_state_dict(state_dict, strict=False)
print(f"Missing keys : {len(missing)}")
print(f"Unexpected keys: {len(unexpected)}")
if missing:
    print("  (missing)", missing[:5])

# ── 6. Save outputs ───────────────────────────────────────────────────────────
OUT_DIR = "/kaggle/working"
torch.save(net.state_dict(), f"{OUT_DIR}/regnety008.pth")
joblib.dump(class_names, f"{OUT_DIR}/class_names.pkl")

size_mb = os.path.getsize(f"{OUT_DIR}/regnety008.pth") / 1024 / 1024
print(f"\nDone!")
print(f"  regnety008.pth  — {size_mb:.1f} MB")
print(f"  class_names.pkl — {len(class_names)} species")
print("\nDownload both files from the Kaggle Output tab.")
