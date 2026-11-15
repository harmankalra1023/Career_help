from typing import Dict, List, Any


def score_assessment(
    instrument_id: str,
    answers: Dict[str, int], # item_id -> 1..5
    items_meta: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Scores psychometric instruments (IPIP Big Five, Holland RIASEC) per PRD §8.3.
    """
    dimension_sums: Dict[str, float] = {}
    dimension_counts: Dict[str, int] = {}

    meta_lookup = {item["id"]: item for item in items_meta}

    for item_id, raw_val in answers.items():
        meta = meta_lookup.get(item_id)
        if not meta:
            continue
        dim = meta.get("dimension", "general")
        rev = meta.get("reverse_scored", False)

        val = (6 - raw_val) if rev else raw_val

        dimension_sums[dim] = dimension_sums.get(dim, 0.0) + val
        dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

    normalized_scores: Dict[str, float] = {}
    for dim, total in dimension_sums.items():
        count = dimension_counts.get(dim, 1)
        # Average is between 1 and 5; normalize to 0..100
        avg = total / count
        norm = round(((avg - 1.0) / 4.0) * 100.0, 1)
        normalized_scores[dim] = max(0.0, min(100.0, norm))

    return normalized_scores
