from datetime import date
from app.services.skills.proficiency import (
    SkillEvidenceItem,
    ProficiencyConfig,
    estimate_proficiency,
)

cfg = ProficiencyConfig(
    half_life_months={"backend": 24, "frontend": 18},
    confidence_norm=1.5,
)
today = date(2026, 11, 15)


def test_empty_evidence():
    p, conf = estimate_proficiency([], cfg, today)
    assert p == 0.0
    assert conf == 0.0


def test_monotonicity():
    e1 = SkillEvidenceItem(
        skill_slug="python",
        category="backend",
        evidence_type="project",
        weight=0.75,
        signal_value=0.5,
        recency_date=date(2026, 10, 1),
    )
    p1, c1 = estimate_proficiency([e1], cfg, today)

    e2 = SkillEvidenceItem(
        skill_slug="python",
        category="backend",
        evidence_type="experience",
        weight=0.9,
        signal_value=0.8,
        recency_date=date(2026, 11, 1),
    )
    p2, c2 = estimate_proficiency([e1, e2], cfg, today)

    assert p2 >= p1
    assert c2 >= c1
    assert 0.0 <= p2 <= 100.0
    assert 0.0 <= c2 <= 1.0
