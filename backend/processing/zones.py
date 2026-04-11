def assign_zones(results):
    zones = ["A", "B", "C"]
    zone_results = []

    n = len(results)
    split = n // 3 + 1

    for i, r in enumerate(results):
        zone = zones[i // split]
        r["zone"] = zone
        zone_results.append(r)

    return zone_results


def zone_counts(zone_results):
    counts = {"A":0, "B":0, "C":0}

    for r in zone_results:
        if r["detected"]:
            counts[r["zone"]] += 1

    return counts


def movement_pattern(counts):
    return " → ".join([z for z, c in counts.items() if c > 0])