from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.simulator.career_simulator import run_career_simulation

router = APIRouter(prefix="/me/simulator", tags=["simulator"])


class SimulationRequest(BaseModel):
    base_salary: float = 75000.0
    current_level: str = "Mid"
    jrs: float = 58.3
    weekly_hours: float = 8.0
    years: int = 4


@router.post("/run")
async def run_simulation(req: SimulationRequest):
    return run_career_simulation(
        base_salary=req.base_salary,
        current_level=req.current_level,
        jrs=req.jrs,
        weekly_hours=req.weekly_hours,
        years=req.years,
        n_simulations=1000
    )
