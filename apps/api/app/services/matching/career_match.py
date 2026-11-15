from typing import Dict, List, Any
import math
from app.services.scoring.engine import get_band


def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    keys = set(v1.keys()).union(set(v2.keys()))
    if not keys:
        return 0.5
    dot = sum(v1.get(k, 0.0) * v2.get(k, 0.0) for k in keys)
    mag1 = math.sqrt(sum(v1.get(k, 0.0) ** 2 for k in keys)) or 1.0
    mag2 = math.sqrt(sum(v2.get(k, 0.0) ** 2 for k in keys)) or 1.0
    return max(0.0, min(1.0, dot / (mag1 * mag2)))


def match_role(
    user_skills: Dict[str, float],
    user_riasec: Dict[str, float],
    role: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes career match score, breakdown, and gap priorities for a given role (PRD §9.5, §9.8).
    """
    required_skills = role.get("required_skills", [])
    if not required_skills:
        return {"match_score": 50.0, "band": "developing", "gaps": []}

    # 1. Skill Fit (weighted coverage of required skills)
    total_importance = sum(r.get("importance", 1.0) for r in required_skills) or 1.0
    weighted_fit_sum = 0.0
    gaps = []

    for req in required_skills:
        slug = req.get("skill_slug")
        min_lvl = req.get("minimum_level", 50.0)
        imp = req.get("importance", 1.0)
        curr = user_skills.get(slug, 0.0)

        fit_ratio = min(1.0, curr / max(1.0, min_lvl))
        weighted_fit_sum += fit_ratio * imp

        if curr < min_lvl:
            deficit = min_lvl - curr
            priority = round((imp * deficit) / 100.0, 2)
            jrs_gain = round(imp * 5.0, 1)
            est_hours = int(math.ceil(deficit * 0.45))
            gaps.append({
                "skill": slug,
                "current": round(curr, 1),
                "required": min_lvl,
                "priority": priority,
                "jrs_gain": jrs_gain,
                "est_hours": est_hours,
            })

    skill_fit = (weighted_fit_sum / total_importance) * 100.0

    # 2. Interest Fit (RIASEC match)
    role_riasec = role.get("riasec", {})
    interest_fit = cosine_similarity(user_riasec, role_riasec) * 100.0 if user_riasec else 70.0

    # Total Match Score: 0.65 * skill_fit + 0.35 * interest_fit
    total_match = round(0.65 * skill_fit + 0.35 * interest_fit, 1)
    gaps_sorted = sorted(gaps, key=lambda g: g["priority"], reverse=True)

    return {
        "role_slug": role.get("slug"),
        "role_title": role.get("title"),
        "match_score": total_match,
        "band": get_band(total_match),
        "skill_fit": round(skill_fit, 1),
        "interest_fit": round(interest_fit, 1),
        "gaps": gaps_sorted,
    }
