"""
Run locally to extract all 5 fold weights from the checkpoint archive.
Usage:
    cd BioSonic/backend
    python model/extract_local.py

Outputs (in model/weights/):
    fold0.pth … fold4.pth   — one clean state dict per fold (~22 MB each)
    class_names.pkl          — 206 species names (if cfg contains them)
"""

import sys, os, types, glob, torch, joblib

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
EXTRACTED   = os.path.join(WEIGHTS_DIR, "extracted")

# ── 0. Stub CFG ───────────────────────────────────────────────────────────────
cfg_mod = types.ModuleType("__main__")
class CFG: pass
cfg_mod.CFG = CFG
sys.modules["__main__"] = cfg_mod

# ── 1. Find fold checkpoints ──────────────────────────────────────────────────
fold_files = sorted(glob.glob(os.path.join(EXTRACTED, "model_fold*.pth")))
if not fold_files:
    raise FileNotFoundError(f"No model_fold*.pth files found in {EXTRACTED}")
print(f"Found {len(fold_files)} fold(s): {[os.path.basename(f) for f in fold_files]}")

os.makedirs(WEIGHTS_DIR, exist_ok=True)

# ── 2. Extract and save each fold's state dict ────────────────────────────────
class_names = None

for i, fold_path in enumerate(fold_files):
    print(f"Processing fold {i}: {os.path.basename(fold_path)} ...", flush=True)
    raw = torch.load(fold_path, map_location="cpu", weights_only=False)

    sd = raw["model_state_dict"]
    out_path = os.path.join(WEIGHTS_DIR, f"fold{i}.pth")
    torch.save(sd, out_path)
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"  Saved → {out_path} ({size_mb:.1f} MB)", flush=True)

    # Try to extract class names from the first fold's cfg
    if class_names is None:
        cfg = raw.get("cfg")
        if cfg:
            for attr in ("class_names", "classes", "bird_names", "target_columns", "labels"):
                val = getattr(cfg, attr, None)
                if val is not None:
                    if isinstance(val, dict):
                        class_names = [k for k, v in sorted(val.items(), key=lambda x: x[1])]
                    else:
                        class_names = list(val)
                    print(f"  Got {len(class_names)} class names from cfg.{attr}", flush=True)
                    break

# ── 3. Save class names (if found in checkpoint) ─────────────────────────────
if class_names:
    out_pkl = os.path.join(WEIGHTS_DIR, "class_names.pkl")
    joblib.dump(class_names, out_pkl)
    print(f"\nSaved class_names.pkl ({len(class_names)} species)")
else:
    print("\nClass names not found in checkpoint.")
    print("Get them from Kaggle with:")
    print("  import pandas as pd, joblib")
    print("  meta = pd.read_csv('/kaggle/input/competitions/birdclef-2026/train_metadata.csv')")
    print("  joblib.dump(sorted(meta['primary_label'].unique().tolist()), 'class_names.pkl')")

print("\nDone! All fold weights extracted.")
