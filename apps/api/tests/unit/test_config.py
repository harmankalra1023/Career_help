from app.core.config import settings, scoring_config


def test_settings_load():
    assert settings.PROJECT_NAME == "Digital Career Twin"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.APP_ENV in ["development", "production", "test"]


def test_scoring_config_load():
    assert "half_life_months" in scoring_config
    assert "evidence_weights" in scoring_config
    assert scoring_config["half_life_months"]["ai_ml"] == 12
