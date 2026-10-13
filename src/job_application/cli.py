"""Small operational CLI for schema setup and source-adapter smoke tests."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict
from datetime import date
from pathlib import Path

from job_application.config import get_settings
from job_application.dashboard import refresh_dashboard_snapshot
from job_application.db.session import build_engine, create_schema
from job_application.domain.models import (
    AshbySourceConfig,
    GoogleCareersSourceConfig,
    GreenhouseSourceConfig,
    JsonObject,
    LeverRegion,
    LeverSourceConfig,
    MicrosoftAiCareersSourceConfig,
    MicrosoftCareersSourceConfig,
    SourceConfig,
    SourceKind,
    WorkdaySourceConfig,
)
from job_application.profiles.ml_systems import match_ml_systems_job
from job_application.profiles.ml_systems.discovery import (
    GOOGLE_CAREERS_ML_SYSTEMS_SEARCH_TEXTS,
    MICROSOFT_AI_ML_SYSTEMS_SEARCH_TEXTS,
    MICROSOFT_AI_ML_SYSTEMS_TITLE_KEYWORDS,
    ML_SYSTEMS_WORKDAY_SEARCH_TEXTS,
    ML_SYSTEMS_WORKDAY_TITLE_KEYWORDS,
)
from job_application.sources.factory import create_source


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="job-application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db = subparsers.add_parser("init-db", help="Create the local database schema")
    init_db.add_argument(
        "--database-url",
        default=None,
        help="SQLAlchemy URL; defaults to JOB_APPLICATION_DATABASE_URL",
    )

    fetch = subparsers.add_parser("fetch", help="Fetch and normalize one public job board")
    _add_source_arguments(fetch)

    match = subparsers.add_parser(
        "match", help="Fetch one board and keep ML systems / training-infrastructure matches"
    )
    _add_source_arguments(match)
    match.add_argument(
        "--summary",
        action="store_true",
        help="Print only fields needed for reviewing or building a local dashboard snapshot",
    )
    match.add_argument(
        "--include-rejected",
        action="store_true",
        help="Include rejected jobs and their reasons for rule auditing",
    )
    match.add_argument(
        "--titles-only",
        action="store_true",
        help="With --include-rejected, print only titles and match decisions",
    )

    refresh_dashboard = subparsers.add_parser(
        "refresh-dashboard",
        help="Refresh the local Role Radar TypeScript snapshot",
    )
    refresh_dashboard.add_argument(
        "--output",
        type=Path,
        default=Path("frontend/app/jobs.ts"),
        help="TypeScript snapshot path (default: frontend/app/jobs.ts)",
    )
    refresh_dashboard.add_argument(
        "--snapshot-date",
        type=date.fromisoformat,
        default=None,
        help="Snapshot date in YYYY-MM-DD format (default: today)",
    )
    serve = subparsers.add_parser("serve", help="Run the local dashboard persistence API")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--output", type=Path, default=Path("frontend/app/jobs.ts"))
    return parser


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "source",
        choices=[kind.value for kind in SourceKind if kind is not SourceKind.OFFICIAL_CAREERS],
    )
    parser.add_argument("company", help="Human-readable company name")
    parser.add_argument(
        "identifier",
        help=(
            "Greenhouse token, Lever site, Ashby board name, Google Careers company filter, "
            "Microsoft careers domain, or Workday TENANT/SITE"
        ),
    )
    parser.add_argument(
        "--lever-region",
        choices=[region.value for region in LeverRegion],
        default="global",
    )
    parser.add_argument(
        "--include-unlisted", action="store_true", help="Include unlisted Ashby posts"
    )
    parser.add_argument(
        "--no-compensation", action="store_true", help="Skip Ashby compensation data"
    )
    parser.add_argument(
        "--search-text",
        action="append",
        default=[],
        help="Repeatable server-side search text for Google, Microsoft, or Workday sources",
    )
    parser.add_argument(
        "--candidate-title-keyword",
        action="append",
        default=[],
        help="Repeatable Microsoft or Workday title keyword used before fetching job details",
    )
    parser.add_argument(
        "--discovery-profile",
        choices=["ml-systems"],
        default=None,
        help="Use provider query terms for a known matching profile",
    )


def _source_config(args: argparse.Namespace) -> SourceConfig:
    source = SourceKind(args.source)
    if source is SourceKind.GREENHOUSE:
        return GreenhouseSourceConfig(company_name=args.company, board_token=args.identifier)
    if source is SourceKind.LEVER:
        return LeverSourceConfig(
            company_name=args.company,
            site=args.identifier,
            region=LeverRegion(args.lever_region),
        )
    if source is SourceKind.GOOGLE_CAREERS:
        google_profile_search_texts = (
            GOOGLE_CAREERS_ML_SYSTEMS_SEARCH_TEXTS if args.discovery_profile == "ml-systems" else ()
        )
        return GoogleCareersSourceConfig(
            company_name=args.company,
            company_filter=args.identifier,
            search_texts=tuple(args.search_text) or google_profile_search_texts,
            max_pages=1 if args.discovery_profile == "ml-systems" else 20,
            allow_partial_results=args.discovery_profile == "ml-systems",
        )
    if source is SourceKind.MICROSOFT_CAREERS:
        microsoft_profile_search_texts = (
            MICROSOFT_AI_ML_SYSTEMS_SEARCH_TEXTS if args.discovery_profile == "ml-systems" else ()
        )
        microsoft_profile_title_keywords = (
            MICROSOFT_AI_ML_SYSTEMS_TITLE_KEYWORDS if args.discovery_profile == "ml-systems" else ()
        )
        return MicrosoftCareersSourceConfig(
            company_name=args.company,
            domain=args.identifier,
            search_texts=tuple(args.search_text) or microsoft_profile_search_texts,
            candidate_title_keywords=(
                tuple(args.candidate_title_keyword) or microsoft_profile_title_keywords
            ),
            required_description_text=(
                "Microsoft AI" if args.discovery_profile == "ml-systems" else None
            ),
        )
    if source is SourceKind.MICROSOFT_AI_CAREERS:
        return MicrosoftAiCareersSourceConfig(
            company_name=args.company,
            required_any_texts=(
                ("superintelligence team", "superintelligence lab")
                if args.discovery_profile == "ml-systems"
                else ()
            ),
        )
    if source is SourceKind.WORKDAY:
        identifier_parts = args.identifier.split("/", maxsplit=1)
        if len(identifier_parts) != 2 or not all(identifier_parts):
            raise SystemExit("Workday identifier must use TENANT/SITE format")
        tenant, site = identifier_parts
        workday_profile_search_texts = (
            ML_SYSTEMS_WORKDAY_SEARCH_TEXTS if args.discovery_profile == "ml-systems" else ()
        )
        profile_title_keywords = (
            ML_SYSTEMS_WORKDAY_TITLE_KEYWORDS if args.discovery_profile == "ml-systems" else ()
        )
        return WorkdaySourceConfig(
            company_name=args.company,
            tenant=tenant,
            site=site,
            search_texts=tuple(args.search_text) or workday_profile_search_texts,
            candidate_title_keywords=(
                tuple(args.candidate_title_keyword) or profile_title_keywords
            ),
        )
    return AshbySourceConfig(
        company_name=args.company,
        job_board_name=args.identifier,
        include_compensation=not args.no_compensation,
        include_unlisted=args.include_unlisted,
    )


async def _fetch(args: argparse.Namespace) -> int:
    config = _source_config(args)
    source = create_source(config)
    jobs = await source.list_jobs(config)
    payload = [{**job.normalized_payload(), "content_hash": job.content_hash()} for job in jobs]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


async def _match(args: argparse.Namespace) -> int:
    config = _source_config(args)
    source = create_source(config)
    jobs = await source.list_jobs(config)
    decisions = []
    for job in jobs:
        result = match_ml_systems_job(job)
        if result.matched or args.include_rejected:
            decisions.append((job, result))
    decisions.sort(key=lambda pair: (-pair[1].score, pair[0].title))

    payload: list[JsonObject] = []
    for job, result in decisions:
        if args.titles_only:
            payload.append(
                {
                    "title": job.title,
                    "match": asdict(result),
                }
            )
        elif args.summary:
            payload.append(
                {
                    "external_id": job.external_id,
                    "company_name": job.company_name,
                    "title": job.title,
                    "locations": job.locations,
                    "job_url": job.job_url,
                    "compensation": (
                        job.compensation.summary if job.compensation is not None else None
                    ),
                    "match": asdict(result),
                }
            )
        else:
            payload.append({**job.normalized_payload(), "match": asdict(result)})
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


async def _refresh_dashboard(args: argparse.Namespace) -> int:
    from job_application.tracking import Tracker

    snapshot_date = args.snapshot_date or date.today()
    jobs = await refresh_dashboard_snapshot(args.output, snapshot_date)
    counts = Counter(job.job.company_name for job in jobs)
    tracker = Tracker()
    try:
        sources = tracker.dashboard()["sources"]
    finally:
        tracker.engine.dispose()
    payload = {
        "output": str(args.output),
        "snapshot_date": snapshot_date.isoformat(),
        "total": len(jobs),
        "companies": dict(counts),
        "sources": sources,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 2 if any(source["status"] == "failed" for source in sources) else 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the project CLI."""

    args = _parser().parse_args(argv)
    if args.command == "init-db":
        database_url = args.database_url or get_settings().database_url
        engine = build_engine(database_url)
        try:
            create_schema(engine)
        finally:
            engine.dispose()
        print(f"Database schema created: {database_url}")
        return 0
    if args.command == "fetch":
        return asyncio.run(_fetch(args))
    if args.command == "match":
        return asyncio.run(_match(args))
    if args.command == "refresh-dashboard":
        _upgrade_database()
        return asyncio.run(_refresh_dashboard(args))
    if args.command == "serve":
        from job_application.api import serve

        _upgrade_database()
        serve(args.output, args.port)
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


def _upgrade_database() -> None:
    from alembic import command
    from alembic.config import Config

    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))
    command.upgrade(config, "head")
