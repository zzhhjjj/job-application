"""Build the local TypeScript dashboard snapshot from live public job boards."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from job_application.domain.models import (
    AmazonJobsSourceConfig,
    AppleCareersSourceConfig,
    AshbySourceConfig,
    DiscoveredJob,
    GoogleCareersSourceConfig,
    GreenhouseSourceConfig,
    MicrosoftAiCareersSourceConfig,
    OfficialCareersSourceConfig,
    OfficialPosting,
    SourceConfig,
    SourceKind,
    WorkdaySourceConfig,
)
from job_application.profiles.ml_systems import MatchTrack, RuleMatch, match_ml_systems_job
from job_application.profiles.ml_systems.discovery import (
    GOOGLE_CAREERS_ML_SYSTEMS_SEARCH_TEXTS,
    ML_SYSTEMS_WORKDAY_SEARCH_TEXTS,
    ML_SYSTEMS_WORKDAY_TITLE_KEYWORDS,
)
from job_application.sources.factory import create_source

_US_LOCATION = re.compile(
    r"\b(?:United States(?: of America)?|USA|U\.S\.)\b|"
    r"(?:^|[\s,|·])US(?:$|[\s,|·])|"
    r",\s*(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|"
    r"MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|"
    r"TX|UT|VT|VA|WA|WV|WI|WY|DC)\b|"
    r"\b(?:San Francisco|New York(?: City)?|Seattle|Mountain View|Santa Clara|"
    r"Palo Alto|Austin|Boston|Westford|Durham|Redmond)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DashboardSource:
    """One company board included in the local Role Radar snapshot."""

    config: SourceConfig
    source_label: str
    id_prefix: str
    include_external_ids: frozenset[str] | None = None
    reviewed_title_keywords: tuple[str, ...] = ()
    match_threshold: int = 9
    canonical_job_url_base: str | None = None


@dataclass(frozen=True)
class DashboardJob:
    """A matched job plus the display metadata needed by the dashboard."""

    job: DiscoveredJob
    match: RuleMatch
    source_label: str
    id_prefix: str


DASHBOARD_SOURCES: tuple[DashboardSource, ...] = (
    DashboardSource(
        config=AshbySourceConfig(company_name="OpenAI", job_board_name="openai"),
        source_label="Ashby",
        id_prefix="openai",
    ),
    DashboardSource(
        config=GreenhouseSourceConfig(company_name="Anthropic", board_token="anthropic"),
        source_label="Greenhouse",
        id_prefix="anthropic",
    ),
    DashboardSource(
        config=GreenhouseSourceConfig(company_name="SpaceXAI", board_token="xai"),
        source_label="Greenhouse",
        id_prefix="spacexai",
    ),
    DashboardSource(
        config=AshbySourceConfig(company_name="Cursor", job_board_name="cursor"),
        source_label="Ashby",
        id_prefix="cursor",
        canonical_job_url_base="https://cursor.com/careers",
    ),
    DashboardSource(
        config=GoogleCareersSourceConfig(
            company_name="Google DeepMind",
            company_filter="DeepMind",
            max_total_drift=2,
        ),
        source_label="Google Careers",
        id_prefix="deepmind",
    ),
    DashboardSource(
        config=GoogleCareersSourceConfig(
            company_name="Google",
            company_filter="Google",
            search_texts=GOOGLE_CAREERS_ML_SYSTEMS_SEARCH_TEXTS,
            max_pages=1,
            allow_partial_results=True,
        ),
        source_label="Google Careers",
        id_prefix="google",
        match_threshold=11,
    ),
    DashboardSource(
        config=MicrosoftAiCareersSourceConfig(
            company_name="MAI Superintelligence",
            required_any_texts=(
                "superintelligence team",
                "superintelligence lab",
            ),
        ),
        source_label="Microsoft AI Careers",
        id_prefix="mai-superintelligence",
        reviewed_title_keywords=(
            "AI Data Platform",
            "Data Flywheel Infra",
            "Post Training",
            "Reinforcement Learning Systems",
            "Pretraining Platform",
            "Training Infrastructure",
        ),
        match_threshold=11,
    ),
    DashboardSource(
        config=AshbySourceConfig(
            company_name="Thinking Machines Lab",
            job_board_name="ThinkingMachines",
        ),
        source_label="Ashby",
        id_prefix="thinking-machines",
    ),
    DashboardSource(
        config=AshbySourceConfig(
            company_name="Periodic Labs",
            job_board_name="periodic-labs",
        ),
        source_label="Ashby",
        id_prefix="periodic-labs",
    ),
    DashboardSource(
        config=WorkdaySourceConfig(
            company_name="NVIDIA",
            tenant="nvidia",
            site="NVIDIAExternalCareerSite",
            search_texts=ML_SYSTEMS_WORKDAY_SEARCH_TEXTS,
            candidate_title_keywords=ML_SYSTEMS_WORKDAY_TITLE_KEYWORDS,
        ),
        source_label="Workday",
        id_prefix="nvidia",
    ),
    DashboardSource(
        config=OfficialCareersSourceConfig(
            company_name="Optiver",
            postings=(
                OfficialPosting(
                    external_id="8405271002",
                    title="Machine Learning Performance Engineer",
                    locations=("New York, NY, United States",),
                    job_url=(
                        "https://www.optiver.com/join-us/jobs/technology/new-york/"
                        "machine-learning-performance-engineer/?gh_jid=8405271002"
                    ),
                    description_text=(
                        "Build scalable and robust training pipelines for deep learning; improve "
                        "deep-learning framework internals, remove performance bottlenecks, and "
                        "support large-scale distributed training with CUDA, PyTorch, JAX, XLA, "
                        "Triton, cuDNN, and cuBLAS."
                    ),
                ),
            ),
        ),
        source_label="Official Careers",
        id_prefix="optiver",
    ),
    DashboardSource(
        config=GreenhouseSourceConfig(company_name="Jane Street", board_token="janestreet"),
        source_label="Greenhouse",
        id_prefix="jane-street",
        include_external_ids=frozenset({"6485460002", "7449077002"}),
        match_threshold=5,
    ),
    DashboardSource(
        config=OfficialCareersSourceConfig(
            company_name="HRT",
            postings=(
                OfficialPosting(
                    external_id="7972584",
                    title="AI Research Engineer, Pre-Training",
                    locations=("New York, NY, United States",),
                    job_url=("https://www.hudsonrivertrading.com/careers/job/?gh_jid=7972584"),
                    description_text=(
                        "Build large-scale pre-training systems on GPU clusters, improve "
                        "distributed model training reliability and performance, and collaborate "
                        "with AI researchers on training infrastructure."
                    ),
                ),
            ),
        ),
        source_label="Official Careers",
        id_prefix="hrt",
    ),
    DashboardSource(
        config=OfficialCareersSourceConfig(
            company_name="D. E. Shaw",
            postings=(
                OfficialPosting(
                    external_id="4954",
                    title="Machine Learning Researcher",
                    locations=("New York, NY, United States",),
                    job_url="https://www.deshaw.com/careers/machine-learning-researcher-4954",
                    description_text=(
                        "Design high-performance computational architectures and efficient "
                        "training workflows. Improve ML scalability and reliability using GPU "
                        "programming, PyTorch, JAX, CUDA, XLA, Triton, or PTX."
                    ),
                ),
            ),
        ),
        source_label="Official Careers",
        id_prefix="de-shaw",
    ),
    DashboardSource(
        config=OfficialCareersSourceConfig(
            company_name="Citadel",
            postings=(
                OfficialPosting(
                    external_id="gqs-machine-learning-engineer",
                    title="Global Quantitative Strategies | Machine Learning Engineer",
                    locations=("New York, NY, United States",),
                    job_url=(
                        "https://www.citadel.com/careers/details/"
                        "global-quantitative-strategies-machine-learning-engineer/"
                    ),
                    active_index_url="https://www.citadel.com/career-sitemap.xml",
                    description_text=(
                        "Design, optimize, and scale distributed training, modeling systems, "
                        "training workflows, research tooling, and internal ML libraries using "
                        "high-performance computing."
                    ),
                    retain_on_forbidden=True,
                ),
            ),
        ),
        source_label="Official Careers",
        id_prefix="citadel",
        match_threshold=5,
    ),
    DashboardSource(
        config=OfficialCareersSourceConfig(
            company_name="Meta",
            postings=(
                OfficialPosting(
                    external_id="3414246448833665",
                    title="Software Engineer, Systems ML",
                    locations=(
                        "Sunnyvale, CA, United States",
                        "Bellevue, WA, United States",
                        "Menlo Park, CA, United States",
                        "Remote, US",
                        "New York, NY, United States",
                    ),
                    job_url=("https://www.metacareers.com/profile/job_details/3414246448833665/"),
                    active_index_url="https://www.metacareers.com/jobsearch/sitemap.xml",
                    description_text=(
                        "Build and optimize AI infrastructure, hardware acceleration, ML systems, "
                        "machine-learning frameworks such as PyTorch, GPU architecture, compilers, "
                        "and performance tooling in C++ and Python."
                    ),
                ),
                OfficialPosting(
                    external_id="2236774387100356",
                    title="AI Software Engineer, Systems ML - Wearables AI",
                    locations=("Seattle, WA, United States",),
                    job_url=("https://www.metacareers.com/profile/job_details/2236774387100356/"),
                    active_index_url="https://www.metacareers.com/jobsearch/sitemap.xml",
                    description_text=(
                        "Apply AI infrastructure and hardware acceleration techniques to optimize "
                        "ML systems; develop benchmarks and improve infrastructure and developer "
                        "efficiency across ML frameworks, compilers, runtimes, GPUs, and "
                        "accelerators."
                    ),
                ),
            ),
        ),
        source_label="Official Careers",
        id_prefix="meta",
    ),
    DashboardSource(
        config=AshbySourceConfig(company_name="RadixArk", job_board_name="radixark"),
        source_label="Ashby",
        id_prefix="radixark",
    ),
    DashboardSource(
        config=AshbySourceConfig(company_name="Inferact", job_board_name="inferact"),
        source_label="Ashby",
        id_prefix="inferact",
    ),
    DashboardSource(
        config=AshbySourceConfig(company_name="Cohere", job_board_name="cohere"),
        source_label="Ashby",
        id_prefix="cohere",
    ),
    DashboardSource(
        config=GreenhouseSourceConfig(company_name="Together AI", board_token="togetherai"),
        source_label="Greenhouse",
        id_prefix="together-ai",
    ),
    DashboardSource(
        config=AshbySourceConfig(company_name="Fireworks AI", job_board_name="fireworks"),
        source_label="Ashby",
        id_prefix="fireworks-ai",
    ),
    DashboardSource(
        config=AppleCareersSourceConfig(company_name="Apple"),
        source_label="Apple Careers",
        id_prefix="apple",
    ),
    DashboardSource(
        config=AmazonJobsSourceConfig(
            company_name="Amazon",
            search_texts=(
                "distributed training",
                "training infrastructure",
                "ML systems",
                "CUDA kernel",
            ),
        ),
        source_label="Amazon Jobs",
        id_prefix="amazon",
    ),
    DashboardSource(
        config=MicrosoftAiCareersSourceConfig(
            company_name="Microsoft AI",
            excluded_any_texts=(
                "Superintelligence Team",
                "Microsoft Superintelligence",
                "superintelligence lab",
                "Microsoft Silicon, Cloud Hardware, and Infrastructure Engineering",
                "SCHIE",
            ),
        ),
        source_label="Microsoft AI Careers",
        id_prefix="microsoft-ai",
        match_threshold=11,
    ),
)


async def fetch_dashboard_jobs(
    sources: Sequence[DashboardSource] = DASHBOARD_SOURCES,
) -> list[DashboardJob]:
    """Fetch all configured boards concurrently and retain matching roles."""

    batches = await asyncio.gather(*(_fetch_source(source) for source in sources))
    company_order = {source.config.company_name: index for index, source in enumerate(sources)}
    jobs = [job for batch in batches for job in batch]
    return sorted(
        jobs,
        key=lambda item: (
            company_order[item.job.company_name],
            -item.match.score,
            item.job.title.casefold(),
            item.job.external_id,
        ),
    )


async def _fetch_source(source: DashboardSource) -> list[DashboardJob]:
    adapter = create_source(source.config)
    discovered = await adapter.list_jobs(source.config)
    return match_dashboard_jobs(source, discovered)


def match_dashboard_jobs(
    source: DashboardSource, discovered: Sequence[DiscoveredJob]
) -> list[DashboardJob]:
    """Apply the same dashboard profile to live and persisted source content."""
    matched: list[DashboardJob] = []
    for discovered_job in discovered:
        job = _canonicalize_dashboard_job(source, discovered_job)
        if (
            source.include_external_ids is not None
            and job.external_id not in source.include_external_ids
        ):
            continue
        if not is_us_job(job):
            continue
        decision = match_ml_systems_job(job, threshold=source.match_threshold)
        reviewed_keyword = next(
            (
                keyword
                for keyword in source.reviewed_title_keywords
                if keyword.casefold() in job.title.casefold()
            ),
            None,
        )
        if not decision.matched and reviewed_keyword is not None:
            decision = RuleMatch(
                matched=True,
                score=source.match_threshold,
                tracks=(MatchTrack.TRAINING_INFRA,),
                reasons=("MAIST 官方岗位标题与正文明确属于模型训练或数据基础设施",),
            )
        if not decision.matched and source.include_external_ids is not None:
            decision = RuleMatch(
                matched=True,
                score=9,
                tracks=(MatchTrack.TRAINING_INFRA,),
                reasons=("人工审核确认岗位包含 training infrastructure 工作",),
            )
        if decision.matched:
            matched.append(
                DashboardJob(
                    job=job,
                    match=decision,
                    source_label=source.source_label,
                    id_prefix=source.id_prefix,
                )
            )
    return matched


def _canonicalize_dashboard_job(source: DashboardSource, job: DiscoveredJob) -> DiscoveredJob:
    """Replace stale provider links when a company publishes canonical job pages."""

    if source.canonical_job_url_base is None:
        return job
    slug = re.sub(r"[^a-z0-9]+", "-", job.title.casefold()).strip("-")
    canonical_url = f"{source.canonical_job_url_base.rstrip('/')}/{slug}"
    return job.model_copy(update={"job_url": canonical_url, "apply_url": canonical_url})


def is_us_job(job: DiscoveredJob) -> bool:
    """Return whether at least one advertised location is explicitly in the US."""

    return any(_location_is_us(location) for location in job.locations)


def render_dashboard_typescript(jobs: Sequence[DashboardJob], snapshot_date: date) -> str:
    """Render a deterministic, type-checked TypeScript snapshot."""

    payload = [_dashboard_payload(item) for item in jobs]
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    display_date = snapshot_date.strftime("%Y.%m.%d")
    companies = [source.config.company_name for source in DASHBOARD_SOURCES]
    company_type = " | ".join(json.dumps(company) for company in companies)
    empty_counts = json.dumps(dict.fromkeys(companies, 0), ensure_ascii=False)
    return f'''export type Company = {company_type};

export type MatchTrack =
  | "training-infra"
  | "systems-performance"
  | "kernel-accelerator"
  | "ml-framework";

export type Job = {{
  id: string;
  company: Company;
  title: string;
  location: string;
  compensation?: string;
  source:
    | "Ashby"
    | "Greenhouse"
    | "Google Careers"
    | "Microsoft AI Careers"
    | "Microsoft Careers"
    | "Workday"
    | "Apple Careers"
    | "Amazon Jobs"
    | "Official Careers";
  url: string;
  score: number;
  tracks: readonly MatchTrack[];
  reasons: readonly string[];
}};

export const snapshotDate = "{display_date}";

// Generated from the public boards with the deterministic
// ML systems / training-infrastructure profile in job_application.profiles.ml_systems.
export const jobs: readonly Job[] = {serialized};

export const companyCounts = jobs.reduce<Record<Company, number>>(
  (counts, job) => ({{ ...counts, [job.company]: counts[job.company] + 1 }}),
  {empty_counts},
);
'''


def _dashboard_payload(item: DashboardJob) -> dict[str, object]:
    job = item.job
    payload: dict[str, object] = {
        "id": f"{item.id_prefix}-{job.external_id}",
        "company": job.company_name,
        "title": job.title,
        "location": _display_location(job),
        "source": item.source_label,
        "url": job.job_url,
        "score": item.match.score,
        "tracks": [track.value for track in item.match.tracks],
        "reasons": list(item.match.reasons[:3]),
    }
    if job.compensation is not None and job.compensation.summary:
        payload["compensation"] = job.compensation.summary
    return payload


def _display_location(job: DiscoveredJob) -> str:
    locations = job.locations[:1] if job.source is SourceKind.GREENHOUSE else job.locations
    components = [part.strip() for location in locations for part in location.split("|")]
    us_locations = [part for part in components if _location_is_us(part)]
    return " · ".join(dict.fromkeys(us_locations)) or "US location not listed"


def _location_is_us(location: str) -> bool:
    return _US_LOCATION.search(location) is not None


async def refresh_dashboard_snapshot(output_path: Path, snapshot_date: date) -> list[DashboardJob]:
    """Fetch, render, and atomically replace the local dashboard snapshot."""

    from job_application.tracking import Tracker

    tracker = Tracker()
    try:
        tracker.bootstrap(output_path)
        return await tracker.refresh(output_path, snapshot_date)
    finally:
        tracker.engine.dispose()
