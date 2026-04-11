def split_chunks(y, sr, chunk_duration=5):
    chunk_samples = chunk_duration * sr
    chunks = []

    for i in range(0, len(y), chunk_samples):
        chunk = y[i:i+chunk_samples]
        if len(chunk) == chunk_samples:
            chunks.append(chunk)

    return chunks