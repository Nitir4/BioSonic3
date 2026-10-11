import librosa
import numpy as np


def load_audio(path):
    try:
        samples, rate = librosa.load(path, sr=None)
    except Exception as exc:
        # The decoder boundary distinguishes unreadable uploads from failures
        # later in model inference; details remain in the server traceback.
        raise ValueError('The upload could not be decoded as audio.') from exc
    if len(samples) == 0 or rate <= 0 or not np.isfinite(samples).all():
        raise ValueError('The upload contains no valid audio samples.')
    return samples, rate
