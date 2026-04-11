import os
import glob
import numpy as np
import librosa
import torch
import timm
import joblib

# ── Config ────────────────────────────────────────────────────────────────────
WEIGHTS_DIR      = os.environ.get("WEIGHTS_DIR",      "model/weights")
CLASS_NAMES_PATH = os.environ.get("CLASS_NAMES_PATH", "model/weights/class_names.pkl")
ID_TO_NAME_PATH  = os.environ.get("ID_TO_NAME_PATH",  "model/weights/id_to_name.pkl")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Mel-spectrogram config (must match training)
SAMPLE_RATE = 32000
N_MELS      = 128
HOP_LENGTH  = 512
N_FFT       = 1024
FMIN        = 20
FMAX        = 16000
IMG_SIZE    = 224

# GLOBALS
fold_models  = []   # list of loaded BirdModel instances
class_names  = []   # iNat taxon IDs in model output order
id_to_name   = {}   # iNat ID → common name (e.g. "Common Kingfisher")


# ── AUDIO → MEL SPECTROGRAM ───────────────────────────────────────────────────
def audio_to_melspec(audio, sr):
    """Convert raw audio to a (1, 1, IMG_SIZE, IMG_SIZE) tensor."""
    if sr != SAMPLE_RATE:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)

    if len(audio) < N_FFT:
        audio = np.pad(audio, (0, N_FFT - len(audio)))

    mel = librosa.feature.melspectrogram(
        y=audio, sr=SAMPLE_RATE,
        n_fft=N_FFT, hop_length=HOP_LENGTH,
        n_mels=N_MELS, fmin=FMIN, fmax=FMAX,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_db = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min() + 1e-6)

    import cv2
    mel_img = cv2.resize(mel_db.astype(np.float32), (IMG_SIZE, IMG_SIZE),
                         interpolation=cv2.INTER_LINEAR)

    # Single-channel input — model was trained on grayscale mel spectrograms
    tensor = torch.from_numpy(mel_img).float().unsqueeze(0)  # (1, H, W)
    return tensor.unsqueeze(0)  # (1, 1, H, W)


# ── MODEL ARCHITECTURE ────────────────────────────────────────────────────────
class BirdModel(torch.nn.Module):
    """
    Mirrors the original training script:
      backbone = timm.create_model('regnety_008', in_chans=1, num_classes=0)
      classifier = nn.Linear(backbone.num_features, num_classes)
    """
    def __init__(self, num_classes: int):
        super().__init__()
        self.backbone = timm.create_model(
            "regnety_008",
            pretrained=False,
            num_classes=0,
            in_chans=1,          # single-channel mel spectrogram
            global_pool="avg",
        )
        self.classifier = torch.nn.Linear(self.backbone.num_features, num_classes)

    def forward(self, x):
        return self.classifier(self.backbone(x))


def _load_single_fold(weight_path: str, num_classes: int) -> BirdModel:
    net = BirdModel(num_classes=num_classes)
    sd = torch.load(weight_path, map_location=DEVICE, weights_only=True)
    missing, unexpected = net.load_state_dict(sd, strict=False)
    if missing:
        print(f"  [{os.path.basename(weight_path)}] missing keys: {len(missing)}")
    if unexpected:
        print(f"  [{os.path.basename(weight_path)}] unexpected keys: {len(unexpected)}")
    net.to(DEVICE)
    net.eval()
    return net


# ── LOAD ALL FOLD MODELS ──────────────────────────────────────────────────────
def load_model():
    global fold_models, class_names, id_to_name

    # Class names (iNat taxon IDs)
    if not os.path.isfile(CLASS_NAMES_PATH):
        print(f"WARNING: class names not found at '{CLASS_NAMES_PATH}'. /predict will return 503.")
        return
    class_names = joblib.load(CLASS_NAMES_PATH)
    num_classes  = len(class_names)
    print(f"Loaded {num_classes} class names.")

    # Human-readable name mapping (optional but recommended)
    if os.path.isfile(ID_TO_NAME_PATH):
        id_to_name = joblib.load(ID_TO_NAME_PATH)
        print(f"Loaded id→name mapping ({len(id_to_name)} entries).")
    else:
        print(f"No id_to_name.pkl found — will return raw taxon IDs.")

    # Find fold weight files: fold0.pth, fold1.pth, …
    fold_paths = sorted(glob.glob(os.path.join(WEIGHTS_DIR, "fold*.pth")))

    if not fold_paths:
        print(f"WARNING: No fold*.pth files found in '{WEIGHTS_DIR}'. /predict will return 503.")
        return

    print(f"Loading {len(fold_paths)} fold model(s) onto {DEVICE} ...")
    for path in fold_paths:
        print(f"  Loading {os.path.basename(path)} ...", flush=True)
        fold_models.append(_load_single_fold(path, num_classes))

    print(f"Ensemble ready: {len(fold_models)} fold(s) × {num_classes} classes.")


# ── ENSEMBLE PREDICT ──────────────────────────────────────────────────────────
def predict(audio_chunk: np.ndarray, sr: int):
    """
    Run all fold models and average their softmax probabilities (soft voting).

    Returns
    -------
    species    : str    — predicted species name
    confidence : float  — mean ensemble probability for the top class [0, 1]
    """
    if not fold_models:
        raise RuntimeError(
            "No fold models loaded — "
            "ensure model/weights/fold*.pth and class_names.pkl exist."
        )

    mel = audio_to_melspec(audio_chunk, sr).to(DEVICE)

    # Accumulate softmax probabilities across folds
    avg_probs = torch.zeros(len(class_names), device=DEVICE)

    with torch.no_grad():
        for net in fold_models:
            logits = net(mel)                           # (1, num_classes)
            probs  = torch.softmax(logits, dim=1)[0]   # (num_classes,)
            avg_probs += probs

    avg_probs /= len(fold_models)

    idx        = int(avg_probs.argmax().item())
    confidence = float(avg_probs[idx].item())
    taxon_id   = class_names[idx] if idx < len(class_names) else "unknown"

    # Return human-readable common name if available, fall back to taxon ID
    species = id_to_name.get(taxon_id, taxon_id)

    return species, confidence