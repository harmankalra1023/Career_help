from typing import List, Optional
from pydantic import BaseModel


class EducationCreate(BaseModel):
    institution: str
    level: str
    degree: str
    branch: Optional[str] = None
    start_year: int
    end_year: Optional[int] = None
    status: str = "completed"
    grade_type: Optional[str] = None
    grade_value: Optional[float] = None
    grade_normalized: Optional[float] = None
    relevant_courses: List[str] = []


class ExperienceCreate(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    employment_type: str = "full_time"
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    skills_used: List[str] = []


class ProjectCreate(BaseModel):
    title: str
    description: str
    url: Optional[str] = None
    repo_url: Optional[str] = None
    skills_used: List[str] = []


class ProfileCompletenessResponse(BaseModel):
    completeness: float # 0.0 to 1.0
    completed_sections: List[str]
    missing_sections: List[str]
