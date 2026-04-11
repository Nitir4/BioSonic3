from processing.audio_loader import load_audio
from processing.chunking import split_chunks
from processing.rai import calculate_rai
from processing.zones import assign_zones, zone_counts, movement_pattern
from model.predictor import predict, load_model
from config import CHUNK_DURATION, CONF_THRESHOLD


def summarize_results(results):
    """Collapse chunk-level predictions into one file-level summary."""
    if not results:
        return {
            "species": "No detection",
            "confidence": 0.0,
            "detected": False,
            "rai": 0,
            "zones": {"A": 0, "B": 0, "C": 0},
            "movement": "None",
        }

    detected_results = [r for r in results if r["detected"]]
    ranked_results = detected_results if detected_results else results
    top_result = max(ranked_results, key=lambda r: r["confidence"])

    rai = calculate_rai(results, CHUNK_DURATION)
    zone_results = assign_zones(results)
    counts = zone_counts(zone_results)
    movement = movement_pattern(counts) or "None"

    return {
        "species": top_result["species"],
        "confidence": round(top_result["confidence"], 4),
        "detected": bool(detected_results),
        "rai": round(rai, 2),
        "zones": counts,
        "movement": movement,
    }


def run_pipeline(audio_path):
    # Load audio
    y, sr = load_audio(audio_path)

    # Split into chunks
    chunks = split_chunks(y, sr, CHUNK_DURATION)

    results = []

    # Run prediction on each chunk
    for i, chunk in enumerate(chunks):
        species, confidence = predict(chunk, sr)

        detected = 1 if confidence > CONF_THRESHOLD else 0

        results.append({
            "chunk": i,
            "species": species,
            "confidence": confidence,
            "detected": detected
        })

    return summarize_results(results)


if __name__ == "__main__":
    # Load model ONCE
    load_model()

    import os

    # pick one audio file automatically
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

    # run pipeline
    output = run_pipeline(sample_path)
    print(output)
