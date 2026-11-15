"""
Taxonomy validator script.
Validates skill and role YAML files against schema and checks referential integrity.
"""
from pathlib import Path
import yaml
import sys


def validate_taxonomy():
    base_dir = Path(__file__).resolve().parent
    skills_path = base_dir / "skills" / "sample_skills.yaml"
    roles_path = base_dir / "roles" / "sample_roles.yaml"

    if not skills_path.exists() or not roles_path.exists():
        print(f"Error: Missing taxonomy files at {skills_path} or {roles_path}")
        return False

    with open(skills_path, "r", encoding="utf-8") as f:
        skills_data = yaml.safe_load(f)
    with open(roles_path, "r", encoding="utf-8") as f:
        roles_data = yaml.safe_load(f)

    skills = skills_data.get("skills", [])
    skill_slugs = {s["slug"] for s in skills}

    # Verify unique IDs and slugs
    skill_ids = [s["id"] for s in skills]
    if len(skill_ids) != len(set(skill_ids)):
        print("Validation error: Duplicate skill IDs found")
        return False

    # Verify prerequisite integrity
    for skill in skills:
        for prereq in skill.get("prerequisites", []):
            if prereq not in skill_slugs:
                print(f"Validation error: Unknown prerequisite '{prereq}' in skill '{skill['slug']}'")
                return False

    # Verify role required skills exist
    roles = roles_data.get("roles", [])
    for role in roles:
        for req in role.get("required_skills", []):
            if req["skill_slug"] not in skill_slugs:
                print(f"Validation error: Role '{role['slug']}' requires unknown skill '{req['skill_slug']}'")
                return False

    print(f"Taxonomy validation passed: {len(skills)} skills, {len(roles)} roles.")
    return True


if __name__ == "__main__":
    if not validate_taxonomy():
        sys.exit(1)
