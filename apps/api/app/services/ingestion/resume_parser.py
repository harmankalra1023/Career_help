import re
from typing import Dict, List, Any


KNOWN_SKILLS_KEYWORDS = {
    "python": ["python", "py", "django", "flask", "fastapi"],
    "fastapi": ["fastapi", "starlette"],
    "docker": ["docker", "container", "containerization", "docker-compose"],
    "kubernetes": ["kubernetes", "k8s"],
    "postgresql": ["postgres", "postgresql", "psql", "sql"],
    "redis": ["redis", "caching"],
    "react": ["react", "reactjs", "react.js"],
    "typescript": ["typescript", "ts"],
    "git": ["git", "github", "gitlab"],
    "system-design": ["microservices", "distributed systems", "system design", "architecture", "rest api"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
}


def parse_resume_text(text: str) -> Dict[str, Any]:
    """
    Ingests and normalizes unstructured resume text into validated profile entities (PRD §7.2).
    """
    text_lower = text.lower()

    # 1. Skill Extraction
    extracted_skills = []
    for slug, keywords in KNOWN_SKILLS_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                extracted_skills.append(slug)
                break

    # 2. Section Chunking Heuristics
    has_degree = bool(re.search(r'\b(bachelor|b\.tech|b\.e|master|m\.tech|phd|degree)\b', text_lower))
    has_experience = bool(re.search(r'\b(engineer|developer|intern|internship|experience|work history)\b', text_lower))
    has_projects = bool(re.search(r'\b(project|built|developed|repository|github)\b', text_lower))

    return {
        "extracted_skills": extracted_skills,
        "education_detected": has_degree,
        "experience_detected": has_experience,
        "projects_detected": has_projects,
        "word_count": len(text.split()),
        "confidence": 0.85 if (has_degree and extracted_skills) else 0.60
    }
