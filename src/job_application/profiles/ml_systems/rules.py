"""Explainable rules for the ML systems and training-infrastructure profile."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from job_application.domain.models import DiscoveredJob


class MatchTrack(StrEnum):
    """High-level areas used to explain why a role was selected."""

    TRAINING_INFRA = "training-infra"
    SYSTEMS_PERFORMANCE = "systems-performance"
    KERNEL_ACCELERATOR = "kernel-accelerator"
    ML_FRAMEWORK = "ml-framework"


@dataclass(frozen=True)
class RuleMatch:
    """A deterministic match decision with score and human-readable evidence."""

    matched: bool
    score: int
    tracks: tuple[MatchTrack, ...]
    reasons: tuple[str, ...]
    excluded_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Signal:
    label: str
    pattern: re.Pattern[str]
    score: int
    track: MatchTrack


def _signal(label: str, pattern: str, score: int, track: MatchTrack) -> _Signal:
    return _Signal(label, re.compile(pattern, re.IGNORECASE), score, track)


_TITLE_SIGNALS = (
    _signal(
        "标题明确包含 training infrastructure",
        r"\btraining\b.*\binfra(?:structure)?\b",
        12,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "标题明确包含 training runtime",
        r"\btraining\b.*\bruntime\b",
        12,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "标题明确包含 training performance",
        r"\btraining\b.*\bperformance\b",
        12,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
    _signal(
        "标题明确包含 distributed training",
        r"\bdistributed\b.*\btraining\b",
        11,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "标题明确包含 training framework",
        r"\btraining\b.*\bframeworks?\b",
        12,
        MatchTrack.ML_FRAMEWORK,
    ),
    _signal(
        "标题明确包含 SFT / fine-tuning systems",
        r"\b(?:SFT|supervised fine[- ]tuning|fine[- ]tuning|post[- ]training)\b"
        r".{0,50}\b(?:infra(?:structure)?|systems?|frameworks?|runtime|performance)\b",
        11,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "标题明确包含 ML systems",
        r"\b(?:ml|machine learning) systems?\b|\bsystems? (?:ml|machine learning)\b",
        11,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "标题提到 ML infrastructure",
        r"\b(?:ml|machine learning) infra(?:structure)?\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "标题明确包含 ML framework",
        r"\b(?:ml|machine learning)\b.*\bframework\b",
        11,
        MatchTrack.ML_FRAMEWORK,
    ),
    _signal(
        "岗位聚焦 ML compiler",
        r"\b(?:ml|machine learning) compilers?\b",
        11,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "岗位聚焦 TPU performance",
        r"\btpu performance\b",
        10,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
    _signal(
        "岗位聚焦 kernel 性能",
        r"\b(?:tpu|gpu|ai|ml) kernels?\b|\bkernel performance\b|"
        r"\bkernels?\s*/\s*cuda\b|\bcuda\s*/\s*kernels?\b",
        10,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "岗位聚焦 AI accelerator",
        r"\baccelerators?\b|hardware codesign",
        10,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "岗位聚焦 ML silicon / chip architecture",
        r"\b(?:ml|ai|genai) (?:silicon|chip)\b|\bsilicon microarchitecture\b",
        9,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "岗位聚焦 workload porting / performance",
        r"\bworkload\b.*\b(?:porting|performance)\b",
        9,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
    _signal(
        "岗位聚焦 research infrastructure",
        r"\bresearch\b.*\binfra(?:structure)?\b",
        9,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "岗位聚焦 pretraining scaling",
        r"\bpre-?training\b.*\bscaling\b",
        9,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "岗位聚焦 pretraining",
        r"\bpre-?training\b",
        9,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "岗位聚焦 post-training",
        r"\bpost-?training\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "岗位聚焦 ML research tooling",
        r"\bresearch tools?\b",
        9,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "岗位以系统性能工程为核心",
        r"\bperformance (?:& systems )?engineer\b|\bsystems & performance engineer\b",
        6,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
)

_DESCRIPTION_SIGNALS = (
    _signal(
        "JD 提到 training infrastructure",
        r"\btraining infrastructure\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 提到 distributed training",
        r"\bdistributed (?:model )?training\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 提到 training runtime",
        r"\btraining runtime\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 提到 training framework",
        r"\btraining frameworks?\b",
        5,
        MatchTrack.ML_FRAMEWORK,
    ),
    _signal(
        "JD 明确属于 RL training infrastructure",
        r"\b(?:RL|reinforcement learning) infrastructure\b",
        6,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 将 distributed training 与 infrastructure 直接关联",
        r"\bdistributed training\b.{0,100}\binfra(?:structure)?\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 提到 SFT / fine-tuning infrastructure",
        r"\b(?:SFT|supervised fine[- ]tuning|fine[- ]tuning|post[- ]training)\b"
        r".{0,80}\b(?:infra(?:structure)?|systems?|frameworks?|runtime|performance)\b",
        5,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 涉及 ML framework internals",
        r"\b(?:ml|machine learning) framework(?: internals?)?\b",
        4,
        MatchTrack.ML_FRAMEWORK,
    ),
    _signal(
        "JD 涉及 learning infrastructure",
        r"\b(?:learning|model training) infrastructure\b",
        4,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 涉及 collective communication",
        r"\bcollective communication\b|\b(?:all-reduce|allreduce)\b",
        4,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
    _signal(
        "JD 涉及底层训练栈",
        r"\b(?:NCCL|OpenXLA|XLA|CUDA|Triton|Pallas|PJRT)\b",
        3,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "JD 涉及 ML accelerator",
        r"\b(?:ml|machine learning|ai) accelerator\b",
        4,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "JD 涉及 compiler / MLIR 优化",
        r"\b(?:compiler|MLIR|JIT compilation|Autograd)\b",
        3,
        MatchTrack.KERNEL_ACCELERATOR,
    ),
    _signal(
        "JD 涉及大规模训练",
        r"\blarge[- ]scale (?:model )?training\b|\btraining at scale\b",
        3,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 涉及训练 pipeline",
        r"\btraining (?:pipeline|platform|system)s?\b",
        3,
        MatchTrack.TRAINING_INFRA,
    ),
    _signal(
        "JD 关注训练吞吐或利用率",
        r"\b(?:training )?(?:throughput|utilization)\b",
        2,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
    _signal(
        "JD 涉及并行、分片或 checkpointing",
        r"\b(?:parallelism|sharding|checkpointing)\b",
        2,
        MatchTrack.SYSTEMS_PERFORMANCE,
    ),
)

_MANAGEMENT_TITLE = re.compile(
    r"\b(?:manager|director|technical program manager|product manager|solutions? architect|"
    r"developer advocate)\b",
    re.IGNORECASE,
)
_CLUSTER_TITLE = re.compile(
    r"\b(?:cluster infrastructure|frontier clusters?|cluster scheduling|resource scheduling|"
    r"gpu infrastructure|compute infrastructure|fleet infrastructure|capacity planning|"
    r"capacity (?:&|and) efficiency infrastructure|ml compute capacity|"
    r"data centers?|site reliability)\b",
    re.IGNORECASE,
)
_ENGINEERING_TITLE = re.compile(r"\b(?:engineer|engineering|architect)\b", re.IGNORECASE)
_TECHNICAL_STAFF_TITLE = re.compile(r"\bMember of Technical Staff\b", re.IGNORECASE)
_TECHNICAL_STAFF_DESCRIPTION = re.compile(r"\bMember of Technical Staff\b", re.IGNORECASE)
_SYSTEMS_RESEARCHER_TITLE = re.compile(r"\bmachine learning researcher\b", re.IGNORECASE)
_SYSTEMS_RESEARCHER_DESCRIPTION = re.compile(
    r"\b(?:training workflows?|training infrastructure|distributed (?:model )?training)\b"
    r".*\b(?:CUDA|XLA|Triton|PTX|GPU programming)\b",
    re.IGNORECASE | re.DOTALL,
)
_INFERENCE_TITLE = re.compile(r"\b(?:inference|local ai platforms?)\b", re.IGNORECASE)
_TRAINING_TITLE = re.compile(
    r"\b(?:training|pre-?training|post-?training|SFT|fine[- ]tuning)\b", re.IGNORECASE
)
_NON_ROLE_TITLE = re.compile(r"\b(?:fellows? program|intern(?:ship)?)\b", re.IGNORECASE)
_UNRELATED_DOMAIN_TITLE = re.compile(
    r"\b(?:security|cybersecurity|consumer devices?|chatgpt|claude code|robotics?|"
    r"autonomous vehicles?|neural reconstruction|formal verification|interpretability|"
    r"knowledge foundations?|discovery|agent harness|network engineer|"
    r"multimodal understanding)\b",
    re.IGNORECASE,
)
_TRAINING_INFRA_DESCRIPTION = re.compile(
    r"\btraining infra(?:structure)?\b|\btraining frameworks?\b|"
    r"\b(?:RL|reinforcement learning) infrastructure\b|"
    r"\bdistributed training\b.{0,100}\binfra(?:structure)?\b",
    re.IGNORECASE | re.DOTALL,
)
_CLUSTER_SCHEDULING_REQUIREMENT = re.compile(
    r"\b(?:strong|deep|extensive|hands-on) experience\b.{0,160}"
    r"\b(?:cluster|job|resource|workload) schedul(?:er|ing)\b",
    re.IGNORECASE | re.DOTALL,
)
_CLUSTER_OPERATIONS_DESCRIPTION = re.compile(
    r"\b(?:TPU|GPU|AI) system control planes?\b|"
    r"\bhealth management systems?\b|"
    r"\b(?:maintain|operate) (?:these )?(?:TPU|GPU|AI) clusters?\b",
    re.IGNORECASE,
)


def match_ml_systems_job(job: DiscoveredJob, *, threshold: int = 9) -> RuleMatch:
    """Match one role to training infrastructure while excluding cluster operations.

    The score is intentionally explainable and deterministic. It is a high-recall gate for a
    later LLM matcher, not a claim that every selected role is equally relevant.
    """

    title = job.title.strip()
    excluded_reasons: list[str] = []
    if _MANAGEMENT_TITLE.search(title):
        excluded_reasons.append("排除管理或项目管理岗位")
    if _CLUSTER_TITLE.search(title):
        excluded_reasons.append("排除 cluster scheduling / fleet / capacity 基础设施岗位")
    if _CLUSTER_SCHEDULING_REQUIREMENT.search(job.description_text):
        excluded_reasons.append("排除明确要求 cluster/job scheduling 专长的岗位")
    if _CLUSTER_OPERATIONS_DESCRIPTION.search(job.description_text):
        excluded_reasons.append("排除 cluster control plane / health operations 岗位")
    if (
        _INFERENCE_TITLE.search(title)
        and not _TRAINING_TITLE.search(title)
        and not _TRAINING_INFRA_DESCRIPTION.search(job.description_text)
    ):
        excluded_reasons.append("排除仅聚焦 inference 的岗位")
    if _NON_ROLE_TITLE.search(title):
        excluded_reasons.append("排除 fellowship 或实习项目")
    if _UNRELATED_DOMAIN_TITLE.search(title):
        excluded_reasons.append("排除标题明确属于其他产品或研究方向的岗位")
    is_systems_researcher = _SYSTEMS_RESEARCHER_TITLE.search(
        title
    ) and _SYSTEMS_RESEARCHER_DESCRIPTION.search(job.description_text)
    is_technical_staff = _TECHNICAL_STAFF_TITLE.search(
        title
    ) or _TECHNICAL_STAFF_DESCRIPTION.search(job.description_text)
    if (
        not _ENGINEERING_TITLE.search(title)
        and not is_systems_researcher
        and not is_technical_staff
    ):
        excluded_reasons.append("排除非工程岗位")

    if excluded_reasons:
        return RuleMatch(
            matched=False,
            score=0,
            tracks=(),
            reasons=(),
            excluded_reasons=tuple(excluded_reasons),
        )

    score = 0
    reasons: list[str] = []
    tracks: list[MatchTrack] = []
    if is_systems_researcher:
        score += 9
        reasons.append("ML researcher 岗位明确包含底层训练系统工作")
        tracks.append(MatchTrack.TRAINING_INFRA)
    for signal in _TITLE_SIGNALS:
        if signal.pattern.search(title):
            score += signal.score
            reasons.append(signal.label)
            if signal.track not in tracks:
                tracks.append(signal.track)

    for signal in _DESCRIPTION_SIGNALS:
        if signal.pattern.search(job.description_text):
            score += signal.score
            reasons.append(signal.label)
            if signal.track not in tracks:
                tracks.append(signal.track)

    return RuleMatch(
        matched=score >= threshold,
        score=score,
        tracks=tuple(tracks),
        reasons=tuple(reasons),
    )
