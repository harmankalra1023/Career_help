from typing import Dict, List, Any
import math


def generate_roadmap(
    target_role: str,
    gaps: List[Dict[str, Any]],
    weekly_hours: float = 8.0,
    horizon_months: int = 6
) -> List[Dict[str, Any]]:
    """
    Capacity-constrained adaptive milestone planner (Technical Design §3.5).
    """
    if not gaps:
        return [
            {
                "id": "ms-mastery-01",
                "sequence_order": 1,
                "title": "Mastery & Advanced Architectural Refactoring",
                "phase": "Growth",
                "month_index": 1,
                "estimated_hours": 20.0,
                "is_locked": False,
                "status": "todo",
                "skills": ["system-design"],
                "resources": [{"title": "Designing Data-Intensive Applications", "type": "book"}],
            }
        ]

    # Capacity per month
    monthly_capacity = max(15.0, weekly_hours * 4.3 * 0.8)

    # Topological prerequisite map
    prereqs = {
        "fastapi": ["python"],
        "docker": [],
        "kubernetes": ["docker"],
        "postgresql": [],
        "redis": [],
        "react": ["typescript"],
        "typescript": [],
    }

    # Order skills considering dependencies
    ordered_gaps = []
    seen = set()

    for gap in gaps:
        skill = gap.get("skill")
        for p in prereqs.get(skill, []):
            if p not in seen:
                ordered_gaps.append({"skill": p, "est_hours": 15.0, "jrs_gain": 3.0})
                seen.add(p)
        if skill not in seen:
            ordered_gaps.append(gap)
            seen.add(skill)

    milestones = []
    current_month = 1
    current_month_hours = 0.0
    seq = 1

    for item in ordered_gaps:
        skill = item.get("skill")
        hours = float(item.get("est_hours", 18.0))
        jrs_gain = float(item.get("jrs_gain", 4.0))

        if (current_month_hours + hours) > monthly_capacity and current_month < horizon_months:
            current_month += 1
            current_month_hours = 0.0

        current_month_hours += hours

        # Assign phase
        ratio = current_month / float(horizon_months)
        if ratio <= 0.30:
            phase = "Foundation"
        elif ratio <= 0.65:
            phase = "Core"
        elif ratio <= 0.85:
            phase = "Applied Projects"
        else:
            phase = "Job Search"

        title = f"{phase}: Master {skill.capitalize()} Fundamentals & Real Projects"

        resources = [
            {"title": f"Interactive {skill.capitalize()} Guided Pathway", "type": "course", "cost": "free"},
            {"title": f"Production {skill.capitalize()} Implementation Project", "type": "project", "cost": "free"},
        ]

        milestones.append({
            "id": f"ms-{seq:02d}",
            "sequence_order": seq,
            "title": title,
            "phase": phase,
            "month_index": current_month,
            "estimated_hours": hours,
            "is_locked": False,
            "status": "in_progress" if seq == 1 else "todo",
            "skills": [skill],
            "resources": resources,
            "expected_jrs_gain": jrs_gain,
        })
        seq += 1

    return milestones
