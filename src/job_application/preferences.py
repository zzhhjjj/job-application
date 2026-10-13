"""Optional private display preferences; never used by discovery or snapshot exports."""

from __future__ import annotations

import json
import logging
from collections.abc import Collection
from pathlib import Path

logger = logging.getLogger(__name__)


def load_company_tiers(path: Path, companies: Collection[str]) -> dict[str, int]:
    """Read the local map on demand. Invalid files must not break the dashboard."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or any(
            company not in companies or type(tier) is not int or tier not in (1, 2)
            for company, tier in data.items()
        ):
            raise ValueError("Expected known company names mapped to 1 or 2")
        return data
    except FileNotFoundError:
        return {}
    except (OSError, ValueError):
        logger.warning("Local company preferences could not be read; showing all companies.")
        return {}
