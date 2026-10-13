from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from job_application.domain.models import (
    AmazonJobsSourceConfig,
    AppleCareersSourceConfig,
    DiscoveredJob,
    GoogleCareersSourceConfig,
    GreenhouseSourceConfig,
    LeverRegion,
    LeverSourceConfig,
    MicrosoftAiCareersSourceConfig,
    MicrosoftCareersSourceConfig,
    SourceKind,
    WorkdaySourceConfig,
    parse_source_config,
)


def _job(**changes: object) -> DiscoveredJob:
    values: dict[str, object] = {
        "source": SourceKind.GREENHOUSE,
        "source_identifier": "example",
        "external_id": "123",
        "company_name": "Example",
        "title": "Research Engineer",
        "locations": [" San Francisco ", "San Francisco", "Remote"],
        "description_text": "Build reliable ML systems.",
        "job_url": "https://example.test/jobs/123",
        "source_updated_at": datetime(2026, 7, 9, tzinfo=UTC),
    }
    values.update(changes)
    return DiscoveredJob.model_validate(values)


def test_discovered_job_normalizes_repeated_strings() -> None:
    job = _job()

    assert job.locations == ("San Francisco", "Remote")


def test_content_hash_ignores_provider_update_timestamp_only() -> None:
    original = _job()
    timestamp_only = _job(source_updated_at=original.source_updated_at + timedelta(days=1))
    changed_title = _job(title="Senior Research Engineer")

    assert original.content_hash() == timestamp_only.content_hash()
    assert original.content_hash() != changed_title.content_hash()


def test_parse_discriminated_source_config() -> None:
    config = parse_source_config(
        {
            "source": "lever",
            "company_name": "Example",
            "site": "example",
            "region": "eu",
        }
    )

    assert isinstance(config, LeverSourceConfig)
    assert config.region is LeverRegion.EU


def test_parse_google_careers_source_config() -> None:
    config = parse_source_config(
        {
            "source": "google-careers",
            "company_name": "Google DeepMind",
            "company_filter": "DeepMind",
        }
    )

    assert isinstance(config, GoogleCareersSourceConfig)
    assert config.company_filter == "DeepMind"


def test_parse_workday_source_config() -> None:
    config = parse_source_config(
        {
            "source": "workday",
            "company_name": "NVIDIA",
            "tenant": "nvidia",
            "site": "NVIDIAExternalCareerSite",
            "search_texts": ["training performance", "NCCL"],
        }
    )

    assert isinstance(config, WorkdaySourceConfig)
    assert config.search_texts == ("training performance", "NCCL")


def test_parse_apple_careers_source_config() -> None:
    config = parse_source_config(
        {
            "source": "apple-careers",
            "company_name": "Apple",
            "team_filter": "machine-learning-infrastructure-MLAI-MLI",
        }
    )

    assert isinstance(config, AppleCareersSourceConfig)


def test_parse_amazon_jobs_source_config() -> None:
    config = parse_source_config(
        {
            "source": "amazon-jobs",
            "company_name": "Amazon",
            "search_texts": ["distributed training"],
        }
    )

    assert isinstance(config, AmazonJobsSourceConfig)


def test_parse_microsoft_careers_source_config() -> None:
    config = parse_source_config(
        {
            "source": "microsoft-careers",
            "company_name": "Microsoft AI",
            "domain": "microsoft.com",
            "search_texts": ["training infrastructure"],
        }
    )

    assert isinstance(config, MicrosoftCareersSourceConfig)
    assert config.search_texts == ("training infrastructure",)


def test_parse_microsoft_ai_careers_source_config() -> None:
    config = parse_source_config(
        {
            "source": "microsoft-ai-careers",
            "company_name": "MAI Superintelligence",
            "required_any_texts": ["superintelligence team"],
        }
    )

    assert isinstance(config, MicrosoftAiCareersSourceConfig)
    assert config.required_any_texts == ("superintelligence team",)


def test_source_config_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        GreenhouseSourceConfig(
            company_name="Example",
            board_token="example",
            unexpected=True,  # type: ignore[call-arg]
        )
