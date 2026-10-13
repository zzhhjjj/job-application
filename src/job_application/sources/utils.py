"""Small dependency-free normalization helpers for source adapters."""

from __future__ import annotations

import hashlib
import html
import re
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any, ClassVar
from urllib.parse import urlparse

from job_application.domain.models import WorkplaceType


class _TextExtractor(HTMLParser):
    _BLOCK_TAGS: ClassVar[set[str]] = {
        "br",
        "div",
        "li",
        "ol",
        "p",
        "section",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag.lower() in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(value: object) -> str:
    """Convert the simple HTML returned by ATS APIs into readable plain text."""

    if not isinstance(value, str) or not value:
        return ""
    decoded = html.unescape(html.unescape(value))
    parser = _TextExtractor()
    parser.feed(decoded)
    parser.close()
    lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line)


def parse_datetime(value: object) -> datetime | None:
    """Parse ISO timestamps and Unix seconds/milliseconds into aware datetimes."""

    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, int | float):
        timestamp = float(value)
        if abs(timestamp) >= 100_000_000_000:
            timestamp /= 1000
        parsed = datetime.fromtimestamp(timestamp, tz=UTC)
    elif isinstance(value, str):
        candidate = value.strip()
        try:
            if candidate.replace(".", "", 1).isdigit():
                return parse_datetime(float(candidate))
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except (OverflowError, ValueError):
            return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def non_empty_string(value: object) -> str | None:
    """Return a trimmed string, accepting scalar IDs from provider payloads."""

    if value is None:
        return None
    result = str(value).strip()
    return result or None


def unique_strings(values: Iterable[object]) -> tuple[str, ...]:
    """Normalize an iterable of possible strings while retaining order."""

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = non_empty_string(value)
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return tuple(result)


def names_from_mappings(values: object, field: str = "name") -> tuple[str, ...]:
    """Read a name-like field from a list of mappings."""

    if not isinstance(values, list):
        return ()
    return unique_strings(item.get(field) for item in values if isinstance(item, Mapping))


def normalize_workplace(value: object, *, is_remote: bool | None = None) -> WorkplaceType:
    """Map provider spellings to the normalized workplace enum."""

    normalized = (non_empty_string(value) or "").lower().replace("_", "").replace("-", "")
    if normalized in {"onsite", "inoffice"}:
        return WorkplaceType.ONSITE
    if normalized == "remote":
        return WorkplaceType.REMOTE
    if normalized == "hybrid":
        return WorkplaceType.HYBRID
    if is_remote is True:
        return WorkplaceType.REMOTE
    return WorkplaceType.UNSPECIFIED


def float_or_none(value: object) -> float | None:
    """Parse a numeric provider value without accepting booleans."""

    if isinstance(value, bool) or not isinstance(value, int | float | str):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def external_id_from_url(url: str, *, fallback_parts: Iterable[str]) -> str:
    """Derive a stable ID when a public API omits an explicit posting ID."""

    path_parts = [part for part in urlparse(url).path.split("/") if part]
    if path_parts:
        if path_parts[-1].lower() in {"application", "apply"} and len(path_parts) > 1:
            return path_parts[-2]
        return path_parts[-1]

    fallback = "\x1f".join(fallback_parts)
    return hashlib.sha256(fallback.encode("utf-8")).hexdigest()[:32]


def ensure_mapping(value: object) -> Mapping[str, Any] | None:
    """Narrow an unknown JSON value to a mapping."""

    return value if isinstance(value, Mapping) else None
