from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Literal, Tuple
import math


def months_between(d1: date, d2: date) -> float:
    return max(0.0, (d2.year - d1.year) * 12 + (d2.month - d1.month) + (d2.day - d1.day) / 30.44)


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(val, max_val))


@dataclass(frozen=True)
class SkillEvidenceItem:
    skill_slug: str
    category: str
    evidence_type: Literal[
        "github", "project", "experience", "certification",
        "education", "assessment", "self_report", "resume_parse"
    ]
    weight: float          # e.g. from config
    signal_value: float    # in [0, 1]
    recency_date: date
    reliability: float = 1.0


@dataclass(frozen=True)
class ProficiencyConfig:
    half_life_months: Dict[str, float]
    confidence_norm: float = 1.5


def estimate_proficiency(
    evidence: List[SkillEvidenceItem],
    cfg: ProficiencyConfig,
    today: date
) -> Tuple[float, float]:
    """
    Pure proficiency estimation algorithm (PRD §7.5 / Technical Design §3.3).
    Returns (proficiency_score [0..100], confidence [0..1.0]).
    """
    if not evidence:
        return 0.0, 0.0

    prod = 1.0
    conf_sum = 0.0

    for e in evidence:
        hl = cfg.half_life_months.get(e.category, 24.0)
        age_m = months_between(e.recency_date, today)
        recency = 0.5 ** (age_m / hl)
        s = clamp(e.signal_value * recency, 0.0, 1.0)
        # Cap single evidence influence at 0.95
        prod *= (1.0 - clamp(e.weight * s, 0.0, 0.95))
        conf_sum += e.weight * s * e.reliability

    p = 100.0 * (1.0 - prod)
    conf = min(1.0, conf_sum / cfg.confidence_norm)
    return round(p, 1), round(conf, 2)
