import json
from pathlib import Path

import pytest

from job_application.preferences import load_company_tiers

COMPANIES = {"Example Company", "Another Company"}


def test_missing_partial_and_removed_preferences(tmp_path: Path) -> None:
    path = tmp_path / "company-tiers.json"
    assert load_company_tiers(path, COMPANIES) == {}
    path.write_text(json.dumps({"Example Company": 2}))
    assert load_company_tiers(path, COMPANIES) == {"Example Company": 2}
    path.write_text(json.dumps({"Another Company": 1}))
    assert load_company_tiers(path, COMPANIES) == {"Another Company": 1}
    path.unlink()
    assert load_company_tiers(path, COMPANIES) == {}


@pytest.mark.parametrize(
    "content",
    [
        "broken",
        "[]",
        "null",
        '{"Unknown": 1}',
        '{"Example Company": true}',
        '{"Example Company": 3}',
        '{"Example Company": "1"}',
        '{"Example Company": 1.0}',
    ],
)
def test_invalid_preferences_fall_back_to_all_companies(tmp_path: Path, content: str) -> None:
    path = tmp_path / "company-tiers.json"
    path.write_text(content)
    assert load_company_tiers(path, COMPANIES) == {}
