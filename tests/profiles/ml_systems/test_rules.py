"""Tests for the deterministic ML systems matching profile."""

from job_application.domain.models import DiscoveredJob, SourceKind
from job_application.profiles.ml_systems import MatchTrack, match_ml_systems_job


def _job(title: str, description: str = "") -> DiscoveredJob:
    return DiscoveredJob(
        source=SourceKind.ASHBY,
        source_identifier="example",
        external_id="role-1",
        company_name="Example AI",
        title=title,
        description_text=description,
        job_url="https://example.test/jobs/role-1",
    )


def test_training_infrastructure_matches_regardless_of_rl_workload_label() -> None:
    result = match_ml_systems_job(_job("Software Engineer, RL Training Infra"))

    assert result.matched
    assert result.score >= 12
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_reinforcement_learning_systems_without_training_infra_does_not_match() -> None:
    result = match_ml_systems_job(
        _job(
            "Reinforcement Learning Systems",
            "Microsoft AI is looking for a Member of Technical Staff to build distributed "
            "systems and resolve performance bottlenecks for large-scale RL training.",
        ),
        threshold=11,
    )

    assert not result.matched


def test_sft_training_infrastructure_is_a_high_confidence_match() -> None:
    result = match_ml_systems_job(_job("Software Engineer, SFT Training Infrastructure"))

    assert result.matched
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_sft_algorithm_role_without_infrastructure_does_not_match() -> None:
    result = match_ml_systems_job(
        _job(
            "Research Engineer, SFT",
            "Develop supervised fine-tuning recipes, curate data, and run model evaluations.",
        )
    )

    assert not result.matched


def test_multimodal_modeling_role_is_excluded_even_when_it_mentions_training_systems() -> None:
    result = match_ml_systems_job(
        _job(
            "Member of Technical Staff - Multimodal Understanding",
            "Build distributed systems for pre-training, SFT, evaluation, and product demos.",
        )
    )

    assert not result.matched
    assert any("其他产品或研究方向" in reason for reason in result.excluded_reasons)


def test_kernel_role_matches_low_level_training_profile() -> None:
    result = match_ml_systems_job(
        _job(
            "TPU Kernel Engineer",
            "Optimize XLA kernels and collective communication for large-scale model training.",
        )
    )

    assert result.matched
    assert MatchTrack.KERNEL_ACCELERATOR in result.tracks
    assert any("底层训练栈" in reason for reason in result.reasons)


def test_kernels_cuda_title_matches_low_level_training_profile() -> None:
    result = match_ml_systems_job(
        _job(
            "Software Engineer - Kernels/CUDA (C++)",
            "Profile large-scale training bottlenecks across GPU memory and multi-GPU systems.",
        )
    )

    assert result.matched
    assert MatchTrack.KERNEL_ACCELERATOR in result.tracks


def test_ml_infrastructure_title_requires_training_evidence() -> None:
    title_only = match_ml_systems_job(_job("Software Engineer, ML Infrastructure"))
    result = match_ml_systems_job(
        _job(
            "Software Engineer, ML Infrastructure",
            "Improve our training framework and the throughput of training runs.",
        )
    )

    assert not title_only.matched
    assert result.matched
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_google_tpu_performance_title_matches_systems_profile() -> None:
    result = match_ml_systems_job(_job("Staff Software Engineer, TPU Performance"))

    assert result.matched
    assert MatchTrack.SYSTEMS_PERFORMANCE in result.tracks


def test_google_ml_compiler_title_matches_accelerator_profile() -> None:
    result = match_ml_systems_job(_job("Staff Software Engineer, ML Compilers, TPU"))

    assert result.matched
    assert MatchTrack.KERNEL_ACCELERATOR in result.tracks


def test_systems_ml_title_matches_systems_profile() -> None:
    result = match_ml_systems_job(_job("Software Engineer, Systems ML"))

    assert result.matched
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_microsoft_member_of_technical_staff_training_role_matches() -> None:
    result = match_ml_systems_job(
        _job(
            "Pre-Training Infrastructure",
            "Microsoft AI is looking for a Member of Technical Staff. Design distributed "
            "training infrastructure and optimize CUDA and NCCL performance.",
        ),
        threshold=11,
    )

    assert result.matched
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_member_of_technical_staff_training_framework_title_is_engineering() -> None:
    result = match_ml_systems_job(
        _job(
            "Member of Technical Staff - RL Training Framework",
            "Develop our RL training framework and optimize end-to-end training performance.",
        )
    )

    assert result.matched
    assert MatchTrack.ML_FRAMEWORK in result.tracks


def test_capacity_efficiency_infrastructure_is_excluded() -> None:
    result = match_ml_systems_job(
        _job(
            "Capacity & Efficiency Infrastructure",
            "Member of Technical Staff building infrastructure for Microsoft AI.",
        )
    )

    assert not result.matched
    assert any("capacity" in reason for reason in result.excluded_reasons)


def test_ml_compute_capacity_is_excluded() -> None:
    result = match_ml_systems_job(
        _job(
            "ML Infrastructure Engineer - ML Compute Capacity",
            "Plan accelerator capacity for a large ML platform.",
        )
    )

    assert not result.matched
    assert any("capacity" in reason for reason in result.excluded_reasons)


def test_unrelated_generic_research_engineer_does_not_match() -> None:
    result = match_ml_systems_job(
        _job("Research Engineer, Model Evaluations", "Build model evaluation datasets.")
    )

    assert not result.matched
    assert result.score == 0


def test_cluster_infrastructure_is_explicitly_excluded() -> None:
    result = match_ml_systems_job(
        _job(
            "Staff Infrastructure Engineer, Cluster Infrastructure",
            "Improve distributed training throughput and GPU utilization.",
        )
    )

    assert not result.matched
    assert result.score == 0
    assert any("cluster scheduling" in reason for reason in result.excluded_reasons)


def test_role_requiring_job_scheduling_expertise_is_excluded() -> None:
    result = match_ml_systems_job(
        _job(
            "Research Engineer, Training Infrastructure",
            "Strong experience with large GPU clusters and job scheduling/orchestration tools.",
        )
    )

    assert not result.matched
    assert any("scheduling 专长" in reason for reason in result.excluded_reasons)


def test_tpu_cluster_health_operations_role_is_excluded() -> None:
    result = match_ml_systems_job(
        _job(
            "Senior Software Engineer, AI/ML System Infrastructure",
            "Build TPU system control planes and health management systems to maintain and "
            "operate TPU clusters.",
        )
    )

    assert not result.matched
    assert any("health operations" in reason for reason in result.excluded_reasons)


def test_inference_only_role_is_excluded() -> None:
    result = match_ml_systems_job(
        _job("Software Engineer, Inference Runtime", "Optimize CUDA kernels for serving.")
    )

    assert not result.matched
    assert any("inference" in reason for reason in result.excluded_reasons)


def test_inference_title_is_allowed_when_jd_explicitly_owns_rl_training_infrastructure() -> None:
    result = match_ml_systems_job(
        _job(
            "Member of Technical Staff - RL Inference",
            "The RL infrastructure team optimizes production training runs using CUDA.",
        )
    )

    assert result.matched
    assert not result.excluded_reasons
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_local_ai_inference_platform_role_is_excluded() -> None:
    result = match_ml_systems_job(
        _job(
            "Senior Software Engineer, GPU Local AI Platforms",
            "Optimize LLM inference throughput, latency, batching, and quantization on edge GPUs.",
        )
    )

    assert not result.matched
    assert any("inference" in reason for reason in result.excluded_reasons)


def test_linux_kernel_security_is_not_treated_as_ml_kernel_work() -> None:
    result = match_ml_systems_job(_job("Senior Security Software Engineer, Linux Kernel Security"))

    assert not result.matched
    assert result.score == 0


def test_description_can_promote_a_generic_engineering_title() -> None:
    result = match_ml_systems_job(
        _job(
            "Research Engineer",
            "Own distributed training and training infrastructure for large-scale training.",
        )
    )

    assert result.matched
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_learning_infrastructure_promotes_embodied_agents_role() -> None:
    result = match_ml_systems_job(
        _job(
            "Research Engineer, Embodied Agents",
            "Design and scale learning infrastructure using distributed training frameworks.",
        )
    )

    assert result.matched
    assert result.score >= 9
    assert MatchTrack.TRAINING_INFRA in result.tracks


def test_ml_chip_architect_matches_accelerator_profile() -> None:
    result = match_ml_systems_job(
        _job(
            "ML Chip/IP Architect",
            "Design a machine learning accelerator and optimize compiler integration.",
        )
    )

    assert result.matched
    assert MatchTrack.KERNEL_ACCELERATOR in result.tracks
