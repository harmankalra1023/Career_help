import numpy as np
from typing import Dict, Any, List


def run_career_simulation(
    base_salary: float = 75000.0,
    current_level: str = "Mid",
    jrs: float = 58.3,
    weekly_hours: float = 8.0,
    years: int = 4,
    n_simulations: int = 1000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Monte Carlo career and salary trajectory simulator (PRD §12, Technical Design §3.6).
    Uses a seeded NumPy RNG for 100% deterministic reproducibility.
    """
    rng = np.random.default_rng(seed)

    # Base yearly salary trajectories array: shape (n_simulations, years + 1)
    trajectories = np.zeros((n_simulations, years + 1))
    trajectories[:, 0] = base_salary

    # Readiness acceleration factor from study hours
    study_boost = min(0.08, (weekly_hours / 10.0) * 0.05)
    effective_readiness = (jrs / 100.0) + study_boost

    promoted_counts = np.zeros(n_simulations)

    for i in range(n_simulations):
        salary = base_salary
        is_promoted = False

        for yr in range(1, years + 1):
            # Base annual merit increase: 3% to 6% normal
            annual_raise = rng.normal(0.045, 0.015)

            # Promotion hazard probability based on readiness and tenure
            promo_hazard = min(0.35, 0.08 + (yr * 0.05) + (effective_readiness * 0.15))

            if not is_promoted and rng.random() < promo_hazard:
                is_promoted = True
                promo_bump = rng.uniform(0.15, 0.25) # 15-25% promotion increase
                annual_raise += promo_bump
                promoted_counts[i] = 1

            salary *= (1.0 + max(0.0, annual_raise))
            trajectories[i, yr] = salary

    # Calculate percentiles across all years
    p10 = [round(float(val)) for val in np.percentile(trajectories, 10, axis=0)]
    p50 = [round(float(val)) for val in np.percentile(trajectories, 50, axis=0)]
    p90 = [round(float(val)) for val in np.percentile(trajectories, 90, axis=0)]

    promotion_probability = round(float(np.mean(promoted_counts)), 2)

    timeline_points = []
    for yr in range(years + 1):
        timeline_points.append({
            "year": f"Year {yr}",
            "p10": p10[yr],
            "p50": p50[yr],
            "p90": p90[yr],
        })

    return {
        "years": years,
        "n_simulations": n_simulations,
        "promotion_probability": promotion_probability,
        "starting_salary": base_salary,
        "projected_median_final": p50[-1],
        "trajectory": timeline_points,
    }
