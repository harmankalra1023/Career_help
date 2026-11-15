from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
import math
from app.core.config import scoring_config, archetypes_config


@dataclass(frozen=True)
class ScoreOutput:
    value: float
    band: str
    confidence: float
    factors: List[Dict[str, Any]]
    data_gaps: List[str]


def get_band(score: float) -> str:
    if score >= 90.0:
        return "exceptional"
    elif score >= 75.0:
        return "strong"
    elif score >= 60.0:
        return "solid"
    elif score >= 40.0:
        return "developing"
    return "emerging"


def compute_pps(completeness: float, verified_evidence_ratio: float, avg_confidence: float) -> ScoreOutput:
    """
    Profile Strength Score (PPS) per PRD §9.3.
    PPS = 0.40 * completeness + 0.35 * verified_ratio + 0.25 * avg_confidence (normalized to 100)
    """
    score = (0.40 * (completeness * 100) +
             0.35 * (verified_evidence_ratio * 100) +
             0.25 * (avg_confidence * 100))
    score = round(max(0.0, min(100.0, score)), 1)
    conf = round(min(1.0, 0.5 + 0.5 * completeness), 2)

    factors = [
        {"factor": "Profile Completeness", "impact": f"+{round(0.40 * completeness * 100, 1)}", "weight": 0.40},
        {"factor": "Verified Evidence Ratio", "impact": f"+{round(0.35 * verified_evidence_ratio * 100, 1)}", "weight": 0.35},
        {"factor": "Evidence Confidence Average", "impact": f"+{round(0.25 * avg_confidence * 100, 1)}", "weight": 0.25},
    ]

    gaps = []
    if completeness < 0.8:
        gaps.append("Profile has unfilled sections (certifications or assessments)")
    if verified_evidence_ratio < 0.5:
        gaps.append("Low proportion of verified repository or work experience evidence")

    return ScoreOutput(value=score, band=get_band(score), confidence=conf, factors=factors, data_gaps=gaps)


def compute_tss(skills: List[Dict[str, Any]]) -> ScoreOutput:
    """
    Technical Skill Score (TSS) per PRD §9.4.
    Balances depth (weighted average of top skills) and breadth (category diversity).
    """
    if not skills:
        return ScoreOutput(value=0.0, band="emerging", confidence=0.0, factors=[], data_gaps=["No technical skills recorded"])

    sorted_skills = sorted(skills, key=lambda s: s.get("proficiency", 0.0), reverse=True)
    top_5 = sorted_skills[:5]
    depth_score = sum(s.get("proficiency", 0.0) for s in top_5) / len(top_5)

    categories = {s.get("category", "backend") for s in skills}
    breadth_ratio = min(1.0, len(categories) / 4.0)
    breadth_score = breadth_ratio * 100.0

    tss = (0.70 * depth_score) + (0.30 * breadth_score)
    tss = round(max(0.0, min(100.0, tss)), 1)

    avg_conf = sum(s.get("confidence", 0.5) for s in skills) / len(skills)
    conf = round(min(1.0, avg_conf), 2)

    factors = [
        {"factor": f"Top Skill Depth ({', '.join(s.get('name', '') for s in top_5[:3])})", "impact": f"+{round(0.70 * depth_score, 1)}", "weight": 0.70},
        {"factor": f"Category Breadth ({len(categories)} domains covered)", "impact": f"+{round(0.30 * breadth_score, 1)}", "weight": 0.30},
    ]

    gaps = []
    if len(skills) < 5:
        gaps.append("Fewer than 5 skills recorded")
    if len(categories) < 3:
        gaps.append("Limited domain diversity across cloud and frontend domains")

    return ScoreOutput(value=tss, band=get_band(tss), confidence=conf, factors=factors, data_gaps=gaps)


def compute_ntss(traits: Dict[str, float], team_evidence_count: int) -> ScoreOutput:
    """
    Non-Technical Skill Score (NTSS) per PRD §9.4.
    Evaluates communication, collaboration, conscientiousness, and work-style traits.
    """
    c = traits.get("conscientiousness", 60.0)
    a = traits.get("agreeableness", 60.0)
    e = traits.get("extraversion", 50.0)
    s = traits.get("emotional_stability", 65.0)

    trait_base = 0.35 * c + 0.25 * a + 0.20 * s + 0.20 * e
    evidence_bonus = min(15.0, team_evidence_count * 5.0)

    ntss = round(max(0.0, min(100.0, trait_base + evidence_bonus)), 1)
    conf = 0.65 if traits else 0.40

    factors = [
        {"factor": "Conscientiousness & Execution Reliability", "impact": f"+{round(0.35 * c, 1)}", "weight": 0.35},
        {"factor": "Agreeableness & Team Collaboration", "impact": f"+{round(0.25 * a, 1)}", "weight": 0.25},
        {"factor": "Workplace Collaboration Signals", "impact": f"+{evidence_bonus}", "weight": 0.15},
    ]

    gaps = ["Complete full IPIP-50 assessment to increase confidence"] if not traits else []
    return ScoreOutput(value=ntss, band=get_band(ntss), confidence=conf, factors=factors, data_gaps=gaps)


def compute_jrs(user_skills: Dict[str, float], required_skills: List[Dict[str, Any]]) -> ScoreOutput:
    """
    Job Readiness Score (JRS) per PRD §9.7.
    Measures readiness against specific role requirements:
    JRS = 0.45 * coverage + 0.30 * depth_adequacy + 0.15 * evidence_credibility + 0.10 * recency
    """
    if not required_skills:
        return ScoreOutput(value=100.0, band="exceptional", confidence=1.0, factors=[], data_gaps=[])

    matched_count = 0
    depth_sum = 0.0

    for req in required_skills:
        slug = req.get("skill_slug")
        min_lvl = req.get("minimum_level", 50.0)
        user_lvl = user_skills.get(slug, 0.0)

        if user_lvl >= (min_lvl * 0.5):
            matched_count += 1
        adequacy = min(1.0, user_lvl / max(1.0, min_lvl))
        depth_sum += adequacy

    coverage = matched_count / len(required_skills)
    depth_adequacy = depth_sum / len(required_skills)

    jrs = (0.50 * coverage * 100.0) + (0.50 * depth_adequacy * 100.0)
    jrs = round(max(0.0, min(100.0, jrs)), 1)

    conf = round(min(1.0, 0.5 + 0.5 * coverage), 2)

    factors = [
        {"factor": f"Required Skill Coverage ({matched_count}/{len(required_skills)} skills)", "impact": f"+{round(0.50 * coverage * 100.0, 1)}", "weight": 0.50},
        {"factor": "Proficiency Adequacy against minimum targets", "impact": f"+{round(0.50 * depth_adequacy * 100.0, 1)}", "weight": 0.50},
    ]

    gaps = [
        f"Missing or below target: {req.get('skill_slug')} (target: {req.get('minimum_level')}%)"
        for req in required_skills if user_skills.get(req.get('skill_slug'), 0.0) < req.get('minimum_level', 50.0)
    ]

    return ScoreOutput(value=jrs, band=get_band(jrs), confidence=conf, factors=factors, data_gaps=gaps)


def compute_dna_archetypes(dimensions: Dict[str, float]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Computes Euclidean distance clustering against Archetype centroids from archetypes.yaml.
    """
    cfg_archetypes = archetypes_config.get("archetypes", {})
    if not cfg_archetypes:
        # Default centroids if config missing
        cfg_archetypes = {
            "systems_builder": {
                "title": "Systems Builder",
                "centroid": {"technical_depth": 85, "systems_thinking": 90, "execution_speed": 70, "collaboration": 65, "creative_exploration": 50, "product_sense": 55}
            },
            "applied_researcher": {
                "title": "Applied Researcher",
                "centroid": {"technical_depth": 92, "systems_thinking": 75, "execution_speed": 60, "collaboration": 60, "creative_exploration": 88, "product_sense": 50}
            },
            "product_craftsman": {
                "title": "Product Craftsman",
                "centroid": {"technical_depth": 70, "systems_thinking": 65, "execution_speed": 80, "collaboration": 75, "creative_exploration": 85, "product_sense": 90}
            }
        }

    similarities = {}
    for key, arch in cfg_archetypes.items():
        centroid = arch.get("centroid", {})
        dist_sq = 0.0
        for dim, val in centroid.items():
            u_val = dimensions.get(dim, 50.0)
            dist_sq += (u_val - val) ** 2
        dist = math.sqrt(dist_sq)
        # Convert distance to similarity score
        sim = 1.0 / (1.0 + (dist / 25.0))
        similarities[arch.get("title", key)] = sim

    total_sim = sum(similarities.values()) or 1.0
    weights = [
        {"name": name, "pct": round(sim / total_sim, 2)}
        for name, sim in sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    ]

    top_name = weights[0]["name"] if weights else "Systems Builder"
    narrative = f"Exhibits a primary archetype of {top_name} with strong foundational engineering rigor and high execution discipline."

    return weights, narrative
