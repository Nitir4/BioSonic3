def calculate_rai(results, chunk_duration):
    total_detections = sum(r["detected"] for r in results)
    total_minutes = (len(results) * chunk_duration) / 60
    
    if total_minutes == 0:
        return 0
    
    return total_detections / total_minutes