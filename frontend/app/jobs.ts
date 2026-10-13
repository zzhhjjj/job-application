export type Company = "OpenAI" | "Anthropic" | "SpaceXAI" | "Cursor" | "Google DeepMind" | "Google" | "MAI Superintelligence" | "Thinking Machines Lab" | "Periodic Labs" | "NVIDIA" | "Optiver" | "Jane Street" | "HRT" | "D. E. Shaw" | "Citadel" | "Meta" | "RadixArk" | "Inferact" | "Cohere" | "Together AI" | "Fireworks AI" | "Apple" | "Amazon" | "Microsoft AI";

export type MatchTrack =
  | "training-infra"
  | "systems-performance"
  | "kernel-accelerator"
  | "ml-framework";

export type Job = {
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
};

export const snapshotDate = "2026.10.09";

// Generated from the public boards with the deterministic
// ML systems / training-infrastructure profile in job_application.profiles.ml_systems.
export const jobs: readonly Job[] = [
  {
    "id": "openai-6eb386ac-9056-4795-aa79-a27e105faf5c",
    "company": "OpenAI",
    "title": "Training Performance Engineer",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/6eb386ac-9056-4795-aa79-a27e105faf5c",
    "score": 50,
    "tracks": [
      "systems-performance",
      "training-infra",
      "ml-framework",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training performance",
      "岗位以系统性能工程为核心",
      "JD 提到 distributed training"
    ],
    "compensation": "$295K - $500K"
  },
  {
    "id": "openai-d8794980-1d3f-4d82-8b48-811449b6c492",
    "company": "OpenAI",
    "title": "Training: ML Framework Engineer",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/d8794980-1d3f-4d82-8b48-811449b6c492",
    "score": 41,
    "tracks": [
      "ml-framework",
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 training framework",
      "标题明确包含 ML framework",
      "JD 提到 training runtime"
    ],
    "compensation": "$295K - $500K"
  },
  {
    "id": "openai-5e4ed6d1-2417-4bf5-bae0-905931c488e3",
    "company": "OpenAI",
    "title": "Software Engineer, Platform Systems",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/5e4ed6d1-2417-4bf5-bae0-905931c488e3",
    "score": 29,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ],
    "compensation": "$380K - $500K"
  },
  {
    "id": "openai-9117987a-7a59-449e-a702-89e8d0e8cb60",
    "company": "OpenAI",
    "title": "Software Engineer,  ML Systems & Training Architecture",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/9117987a-7a59-449e-a702-89e8d0e8cb60",
    "score": 24,
    "tracks": [
      "training-infra",
      "ml-framework"
    ],
    "reasons": [
      "标题明确包含 ML systems",
      "JD 提到 training infrastructure",
      "JD 提到 training framework"
    ],
    "compensation": "$295K - $380K"
  },
  {
    "id": "openai-9248eab6-74e0-4940-98eb-ca09b17da532",
    "company": "OpenAI",
    "title": "Software Engineer, AI accelerator Runtime",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/9248eab6-74e0-4940-98eb-ca09b17da532",
    "score": 19,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 AI accelerator",
      "JD 涉及 ML accelerator",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$266K - $445K"
  },
  {
    "id": "openai-f386b209-1259-4b79-bf5a-aa97fc7ce77b",
    "company": "OpenAI",
    "title": "Software Engineer, Accelerators",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/f386b209-1259-4b79-bf5a-aa97fc7ce77b",
    "score": 15,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 AI accelerator",
      "JD 涉及 compiler / MLIR 优化",
      "JD 涉及并行、分片或 checkpointing"
    ],
    "compensation": "$295K - $380K"
  },
  {
    "id": "openai-ec0a4e03-bbcc-4c64-813f-b53dabb8f53a",
    "company": "OpenAI",
    "title": "Workload Porting & Performance Engineer",
    "location": "San Francisco · Seattle",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/ec0a4e03-bbcc-4c64-813f-b53dabb8f53a",
    "score": 15,
    "tracks": [
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 workload porting / performance",
      "岗位以系统性能工程为核心"
    ],
    "compensation": "$347K - $445K"
  },
  {
    "id": "openai-f3ddd41c-541f-485e-90d6-86c26e018e9f",
    "company": "OpenAI",
    "title": "Software Engineer, GPT Infrastructure",
    "location": "San Francisco · Seattle",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/f3ddd41c-541f-485e-90d6-86c26e018e9f",
    "score": 14,
    "tracks": [
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 涉及 collective communication",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$293K - $385K"
  },
  {
    "id": "openai-348ac6bf-a5c3-43d1-a14a-5f1a3c8d90fa",
    "company": "OpenAI",
    "title": "Software Engineer, Monetization ML Infrastructure",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/348ac6bf-a5c3-43d1-a14a-5f1a3c8d90fa",
    "score": 14,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "标题提到 ML infrastructure",
      "JD 涉及 learning infrastructure",
      "JD 涉及训练 pipeline"
    ],
    "compensation": "$347K - $445K"
  },
  {
    "id": "openai-e9627fa6-ac76-4899-9a93-9251419e61a0",
    "company": "OpenAI",
    "title": "Software Engineer, Kernel Performance & AI Tooling",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/e9627fa6-ac76-4899-9a93-9251419e61a0",
    "score": 13,
    "tracks": [
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 kernel 性能",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$266K - $445K"
  },
  {
    "id": "openai-ec317080-e2d2-4a73-93e6-e0a9ae6fdf96",
    "company": "OpenAI",
    "title": "Software Engineer, Model Runtime",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/ec317080-e2d2-4a73-93e6-e0a9ae6fdf96",
    "score": 11,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 涉及 ML accelerator",
      "JD 涉及 compiler / MLIR 优化",
      "JD 关注训练吞吐或利用率"
    ],
    "compensation": "$266K - $445K"
  },
  {
    "id": "openai-340c0c22-8d8f-4232-b17e-f642b64c25c3",
    "company": "OpenAI",
    "title": "Software Engineer, Collective Communication",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/340c0c22-8d8f-4232-b17e-f642b64c25c3",
    "score": 10,
    "tracks": [
      "systems-performance",
      "kernel-accelerator",
      "training-infra"
    ],
    "reasons": [
      "JD 涉及 collective communication",
      "JD 涉及底层训练栈",
      "JD 涉及训练 pipeline"
    ],
    "compensation": "$380K - $500K"
  },
  {
    "id": "openai-0fc4742f-21f9-40a3-925e-adeb0a6920c1",
    "company": "OpenAI",
    "title": "Training - Runtime Foundations Engineer",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/0fc4742f-21f9-40a3-925e-adeb0a6920c1",
    "score": 27,
    "tracks": [
      "training-infra",
      "ml-framework"
    ],
    "reasons": [
      "标题明确包含 training runtime",
      "JD 提到 distributed training",
      "JD 提到 training runtime"
    ],
    "compensation": "$266K - $385K"
  },
  {
    "id": "openai-bd2b8228-bb0f-42e0-94bd-c853cdd56140",
    "company": "OpenAI",
    "title": "Research Engineer, AI for Chip Design",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/bd2b8228-bb0f-42e0-94bd-c853cdd56140",
    "score": 10,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ],
    "compensation": "$380K - $500K"
  },
  {
    "id": "openai-b2250643-bfd0-4ce6-abbf-cb7e8c8123ba",
    "company": "OpenAI",
    "title": "AI Infrastructure Engineer, pAGI",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/openai/b2250643-bfd0-4ce6-abbf-cb7e8c8123ba",
    "score": 20,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ],
    "compensation": "$266K - $500K"
  },
  {
    "id": "anthropic-4926227008",
    "company": "Anthropic",
    "title": "Performance Engineer, GPU",
    "location": "San Francisco, CA · New York City, NY · Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4926227008",
    "score": 35,
    "tracks": [
      "systems-performance",
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "anthropic-4616971008",
    "company": "Anthropic",
    "title": "Research Engineer/Research Scientist, Pre-training",
    "location": "San Francisco, CA · Seattle, WA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4616971008",
    "score": 21,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 pretraining",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "anthropic-4720576008",
    "company": "Anthropic",
    "title": "TPU Kernel Engineer",
    "location": "San Francisco, CA · New York City, NY · Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4720576008",
    "score": 20,
    "tracks": [
      "kernel-accelerator",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 kernel 性能",
      "JD 涉及 ML framework internals",
      "JD 涉及 collective communication"
    ]
  },
  {
    "id": "anthropic-4938432008",
    "company": "Anthropic",
    "title": "Research Engineer, Pretraining Scaling",
    "location": "San Francisco, CA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4938432008",
    "score": 18,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 pretraining scaling",
      "岗位聚焦 pretraining"
    ]
  },
  {
    "id": "anthropic-5254364008",
    "company": "Anthropic",
    "title": "Research Engineer, Code RL (Reinforcement Learning)",
    "location": "San Francisco, CA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/5254364008",
    "score": 14,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 明确属于 RL training infrastructure",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "anthropic-4020350008",
    "company": "Anthropic",
    "title": "Performance Engineer",
    "location": "San Francisco, CA · New York City, NY · Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4020350008",
    "score": 12,
    "tracks": [
      "systems-performance",
      "ml-framework"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 涉及 ML framework internals",
      "JD 关注训练吞吐或利用率"
    ]
  },
  {
    "id": "anthropic-5364804008",
    "company": "Anthropic",
    "title": "Machine Learning Infrastructure Engineer, Safeguards Research",
    "location": "San Francisco, CA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/5364804008",
    "score": 11,
    "tracks": [
      "training-infra",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "标题提到 ML infrastructure",
      "JD 涉及 ML framework internals",
      "JD 关注训练吞吐或利用率"
    ]
  },
  {
    "id": "anthropic-4613568008",
    "company": "Anthropic",
    "title": "Research Engineer, Machine Learning (Reinforcement Learning)",
    "location": "San Francisco, CA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4613568008",
    "score": 10,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 明确属于 RL training infrastructure",
      "JD 涉及 learning infrastructure"
    ]
  },
  {
    "id": "anthropic-5198108008",
    "company": "Anthropic",
    "title": "Research Engineer, Machine Learning (RL Velocity)",
    "location": "San Francisco, CA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/5198108008",
    "score": 10,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "anthropic-4981828008",
    "company": "Anthropic",
    "title": "Software Engineer, Research Tools",
    "location": "San Francisco, CA · New York City, NY; San Francisco, CA · New York City, NY · Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4981828008",
    "score": 9,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 ML research tooling"
    ]
  },
  {
    "id": "anthropic-4973067008",
    "company": "Anthropic",
    "title": "Pre-training Data Infrastructure Engineer",
    "location": "San Francisco, CA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4973067008",
    "score": 32,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 training infrastructure",
      "岗位聚焦 pretraining",
      "JD 提到 training infrastructure"
    ]
  },
  {
    "id": "anthropic-5283063008",
    "company": "Anthropic",
    "title": "Software Engineer, Research Infrastructure",
    "location": "San Francisco, CA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/5283063008",
    "score": 9,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 research infrastructure"
    ]
  },
  {
    "id": "anthropic-5421263008",
    "company": "Anthropic",
    "title": "Software Engineer, Tokens and Prompt Structures",
    "location": "San Francisco, CA · New York City, NY",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/5421263008",
    "score": 9,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 涉及 learning infrastructure"
    ]
  },
  {
    "id": "anthropic-5438030008",
    "company": "Anthropic",
    "title": "Research Engineer / Performance Engineer, RL Distributed Systems",
    "location": "San Francisco, CA · New York City, NY · Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/5438030008",
    "score": 14,
    "tracks": [
      "systems-performance"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 涉及 collective communication",
      "JD 关注训练吞吐或利用率"
    ]
  },
  {
    "id": "anthropic-4952051008",
    "company": "Anthropic",
    "title": "Research Engineer, RL Engineering",
    "location": "San Francisco, CA · New York City, NY · Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/anthropic/jobs/4952051008",
    "score": 20,
    "tracks": [
      "training-infra",
      "ml-framework"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 SFT / fine-tuning infrastructure",
      "JD 涉及 ML framework internals"
    ]
  },
  {
    "id": "spacexai-5186992007",
    "company": "SpaceXAI",
    "title": "Member of Technical Staff - RL Training Framework",
    "location": "Palo Alto, CA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/xai/jobs/5186992007",
    "score": 28,
    "tracks": [
      "ml-framework",
      "training-infra"
    ],
    "reasons": [
      "标题明确包含 training framework",
      "JD 提到 training infrastructure",
      "JD 提到 training framework"
    ]
  },
  {
    "id": "spacexai-5193037007",
    "company": "SpaceXAI",
    "title": "ML Infrastructure Engineer",
    "location": "Palo Alto, CA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/xai/jobs/5193037007",
    "score": 18,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题提到 ML infrastructure",
      "JD 提到 training infrastructure",
      "JD 提到 training framework"
    ]
  },
  {
    "id": "spacexai-5052040007",
    "company": "SpaceXAI",
    "title": "Software Engineer - Kernels/CUDA (C++)",
    "location": "Palo Alto, CA; Seattle, WA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/xai/jobs/5052040007",
    "score": 13,
    "tracks": [
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 kernel 性能",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "spacexai-5180223007",
    "company": "SpaceXAI",
    "title": "Member of Technical Staff - RL Inference",
    "location": "Palo Alto, CA",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/xai/jobs/5180223007",
    "score": 9,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 明确属于 RL training infrastructure",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "cursor-0aa0650b-f93c-416e-9e2f-4fdf1556fd14",
    "company": "Cursor",
    "title": "Software Engineer, ML Research",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://cursor.com/careers/software-engineer-ml-research",
    "score": 16,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 明确属于 RL training infrastructure",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "cursor-c66cde5e-9cb6-4a2e-a330-9323e1edf2a9",
    "company": "Cursor",
    "title": "Software Engineer, ML Infrastructure",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://cursor.com/careers/software-engineer-ml-infrastructure",
    "score": 12,
    "tracks": [
      "training-infra",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "标题提到 ML infrastructure",
      "JD 提到 training framework",
      "JD 关注训练吞吐或利用率"
    ]
  },
  {
    "id": "cursor-0320a8db-cb1b-407b-bd62-b23734b83330",
    "company": "Cursor",
    "title": "Software Engineer, Pretraining",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://cursor.com/careers/software-engineer-pretraining",
    "score": 11,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 pretraining",
      "JD 关注训练吞吐或利用率"
    ]
  },
  {
    "id": "cursor-c1ac67d4-645a-4632-a178-ea6b5f49bb26",
    "company": "Cursor",
    "title": "Full Stack Engineer, ML Research Tools",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://cursor.com/careers/full-stack-engineer-ml-research-tools",
    "score": 9,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 ML research tooling"
    ]
  },
  {
    "id": "deepmind-102468972783248070",
    "company": "Google DeepMind",
    "title": "Research Engineering Technical Lead, AlphaEarth, DeepMind",
    "location": "New York, NY, USA",
    "source": "Google Careers",
    "url": "https://www.google.com/about/careers/applications/jobs/results/102468972783248070-research-engineering-technical-lead-alphaearth-deepmind?company=DeepMind",
    "score": 15,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ],
    "compensation": "$207,000 - $300,000 (USD)"
  },
  {
    "id": "google-115494592832250566",
    "company": "Google",
    "title": "Machine Learning Hardware Architect, Google Cloud",
    "location": "Sunnyvale, CA, USA",
    "source": "Google Careers",
    "url": "https://www.google.com/about/careers/applications/jobs/results/115494592832250566-machine-learning-hardware-architect-google-cloud?company=Google",
    "score": 12,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 涉及底层训练栈",
      "JD 涉及 ML accelerator",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$163,000 - $236,000 (USD)"
  },
  {
    "id": "google-127729399880393414",
    "company": "Google",
    "title": "Staff SWE, ML Compiler Performance Engineer Co-Design",
    "location": "Mountain View, CA, USA",
    "source": "Google Careers",
    "url": "https://www.google.com/about/careers/applications/jobs/results/127729399880393414-staff-swe-ml-compiler-performance-engineer-co-design?company=Google",
    "score": 23,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 ML compiler",
      "岗位以系统性能工程为核心",
      "JD 涉及底层训练栈"
    ],
    "compensation": "$207,000 - $300,000 (USD)"
  },
  {
    "id": "google-133750920407065286",
    "company": "Google",
    "title": "Senior Software Engineer, ML Compilers, Edge TPU",
    "location": "Mountain View, CA, USA · Kirkland, WA, USA",
    "source": "Google Careers",
    "url": "https://www.google.com/about/careers/applications/jobs/results/133750920407065286-senior-software-engineer-ml-compilers-edge-tpu?company=Google",
    "score": 14,
    "tracks": [
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 ML compiler",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$174,000 - $252,000 (USD)"
  },
  {
    "id": "thinking-machines-93855db2-9a80-421d-9e80-ace9eca24650",
    "company": "Thinking Machines Lab",
    "title": "Research Engineer, Infrastructure, Numerics",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/ThinkingMachines/93855db2-9a80-421d-9e80-ace9eca24650",
    "score": 36,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 research infrastructure",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "thinking-machines-9dabecde-1bdb-47c6-b943-ff7b0526657c",
    "company": "Thinking Machines Lab",
    "title": "Research Engineer, Infrastructure, Training Systems",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/ThinkingMachines/9dabecde-1bdb-47c6-b943-ff7b0526657c",
    "score": 25,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 research infrastructure",
      "JD 提到 distributed training",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "thinking-machines-2d7a9e99-836a-475b-9ae3-b6b1df8baa6d",
    "company": "Thinking Machines Lab",
    "title": "Research Engineer, Infrastructure, Kernels",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/ThinkingMachines/2d7a9e99-836a-475b-9ae3-b6b1df8baa6d",
    "score": 19,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 research infrastructure",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "thinking-machines-0046b97e-6b8d-4dde-8d11-37aed910151a",
    "company": "Thinking Machines Lab",
    "title": "Software Engineer, Supercomputing",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/ThinkingMachines/0046b97e-6b8d-4dde-8d11-37aed910151a",
    "score": 10,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及并行、分片或 checkpointing"
    ]
  },
  {
    "id": "thinking-machines-72fe46e4-a772-4ebb-a413-53e4f1a8273e",
    "company": "Thinking Machines Lab",
    "title": "Software Engineer, Research Tools",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/ThinkingMachines/72fe46e4-a772-4ebb-a413-53e4f1a8273e",
    "score": 17,
    "tracks": [
      "training-infra",
      "ml-framework"
    ],
    "reasons": [
      "岗位聚焦 ML research tooling",
      "JD 提到 training framework",
      "JD 涉及训练 pipeline"
    ]
  },
  {
    "id": "periodic-labs-d9180228-c113-4d5f-a4d6-793994e50b7c",
    "company": "Periodic Labs",
    "title": "ML Systems Engineer",
    "location": "Menlo Park, CA",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/periodic-labs/d9180228-c113-4d5f-a4d6-793994e50b7c",
    "score": 37,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 ML systems",
      "JD 提到 distributed training",
      "JD 明确属于 RL training infrastructure"
    ]
  },
  {
    "id": "periodic-labs-168dbf20-2230-49a0-9f00-f2ff58dad5c8",
    "company": "Periodic Labs",
    "title": "Research Scientist/Research Engineer, Midtraining",
    "location": "Menlo Park, CA",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/periodic-labs/168dbf20-2230-49a0-9f00-f2ff58dad5c8",
    "score": 18,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 涉及大规模训练"
    ]
  },
  {
    "id": "nvidia-JR2015863",
    "company": "NVIDIA",
    "title": "Senior Software Engineer, RL Post-Training Frameworks",
    "location": "US, CA, Santa Clara · US, CA, Remote",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Software-Engineer--RL-Post-Training-Frameworks_JR2015863",
    "score": 55,
    "tracks": [
      "ml-framework",
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 training framework",
      "标题明确包含 SFT / fine-tuning systems",
      "岗位聚焦 post-training"
    ],
    "compensation": "$184,000 - $356,500"
  },
  {
    "id": "nvidia-JR2022034",
    "company": "NVIDIA",
    "title": "Senior Deep Learning Software Infrastructure Engineer",
    "location": "US, CA, Remote",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Remote/Senior-Deep-Learning-Sofware-Infrastructure-Engineer_JR2022034",
    "score": 25,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 涉及 learning infrastructure"
    ],
    "compensation": "$224,000 - $431,250"
  },
  {
    "id": "nvidia-JR2017016",
    "company": "NVIDIA",
    "title": "Principal High-Performance LLM Training Engineer",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Principal-High-Performance-LLM-Training-Engineer_JR2017016",
    "score": 17,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及 ML accelerator"
    ],
    "compensation": "$272,000 - $431,250"
  },
  {
    "id": "nvidia-JR2021938",
    "company": "NVIDIA",
    "title": "Senior AI Training Performance Architect",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-AI-Training-Performance-Architect_JR2021938",
    "score": 15,
    "tracks": [
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training performance",
      "JD 涉及底层训练栈"
    ],
    "compensation": "$184,000 - $356,500"
  },
  {
    "id": "nvidia-JR2022185",
    "company": "NVIDIA",
    "title": "Senior Performance Engineer - DGX Cloud",
    "location": "US, CA, Santa Clara · US, TX, Austin · US, OR, Remote · US, WA, Remote · US, WA, Redmond",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Performance-Engineer---DGX-Cloud_JR2022185",
    "score": 14,
    "tracks": [
      "systems-performance",
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 提到 distributed training",
      "JD 涉及底层训练栈"
    ],
    "compensation": "$224,000 - $431,250"
  },
  {
    "id": "nvidia-JR2014055",
    "company": "NVIDIA",
    "title": "Principal Engineer, CUDA UMD - GPU Kernel Scheduling",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Principal-Engineer--CUDA-UMD---Kernel-Scheduling_JR2014055",
    "score": 13,
    "tracks": [
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 kernel 性能",
      "JD 涉及底层训练栈"
    ],
    "compensation": "$272,000 - $431,250"
  },
  {
    "id": "nvidia-JR2019844",
    "company": "NVIDIA",
    "title": "Senior Deep Learning Compiler Engineer - HW-SW Codesign",
    "location": "US, CA, Santa Clara · US, TX, Austin · US, TX, Remote · US, WA, Remote · US, CA, Remote · US, WA, Redmond",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Deep-Learning-Compiler-Engineer---XLA_JR2019844",
    "score": 13,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$152,000 - $287,500"
  },
  {
    "id": "nvidia-JR2014047",
    "company": "NVIDIA",
    "title": "Senior Performance Engineer - Deep Learning",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Performance-Engineer---Deep-Learning_JR2014047",
    "score": 11,
    "tracks": [
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 涉及底层训练栈",
      "JD 涉及并行、分片或 checkpointing"
    ],
    "compensation": "$152,000 - $287,500"
  },
  {
    "id": "nvidia-JR2013283",
    "company": "NVIDIA",
    "title": "Senior AI Performance and Efficiency Engineer",
    "location": "US, CA, Santa Clara · US, CA, Remote · US, NY, New York · US, WA, Seattle",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-AI-Performance-and-Efficiency-Engineer_JR2013283",
    "score": 10,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 关注训练吞吐或利用率"
    ],
    "compensation": "$152,000 - $287,500"
  },
  {
    "id": "nvidia-JR2014725",
    "company": "NVIDIA",
    "title": "Senior Software Engineer - CUDA Driver",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Software-Engineer---CUDA-Driver_JR2014725",
    "score": 10,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及并行、分片或 checkpointing"
    ],
    "compensation": "$152,000 - $287,500"
  },
  {
    "id": "nvidia-JR2022830",
    "company": "NVIDIA",
    "title": "Senior Software Engineer, CUDA Deep Learning Systems",
    "location": "US, CA, Santa Clara · US, TX, Austin · US, TX, Remote",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Software-Engineer--CUDA-Deep-Learning-Systems_JR2022830",
    "score": 10,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化",
      "JD 关注训练吞吐或利用率"
    ],
    "compensation": "$184,000 - $356,500"
  },
  {
    "id": "nvidia-JR2019246",
    "company": "NVIDIA",
    "title": "Senior Software Engineer, DGX Cloud AI Infrastructure",
    "location": "US, CA, Santa Clara · US, TX, Austin · US, OR, Remote · US, WA, Remote · US, WA, Redmond",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Software-Engineer--DGX-Cloud-AI-Infrastructure_JR2019246",
    "score": 10,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及并行、分片或 checkpointing"
    ],
    "compensation": "$184,000 - $356,500"
  },
  {
    "id": "nvidia-JR2024920",
    "company": "NVIDIA",
    "title": "Senior Software Engineer CUDA UMD - GPU Kernel Scheduling",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Software-Engineer-CUDA-UMD---GPU-Kernel-Scheduling_JR2024920",
    "score": 13,
    "tracks": [
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 kernel 性能",
      "JD 涉及底层训练栈"
    ],
    "compensation": "$152,000 - $287,500"
  },
  {
    "id": "nvidia-JR2025745",
    "company": "NVIDIA",
    "title": "Senior Deep Learning Engineer, Cosmo 3D Spatial",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Deep-Learning-Engineer--Cosmo-3D-Spatial_JR2025745",
    "score": 9,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 关注训练吞吐或利用率",
      "JD 涉及并行、分片或 checkpointing"
    ],
    "compensation": "$224,000 - $356,500"
  },
  {
    "id": "nvidia-JR2026547",
    "company": "NVIDIA",
    "title": "Performance Engineer - Deep Learning",
    "location": "US, CA, Santa Clara",
    "source": "Workday",
    "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Performance-Engineer---Deep-Learning_JR2026547",
    "score": 11,
    "tracks": [
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 涉及底层训练栈",
      "JD 涉及并行、分片或 checkpointing"
    ],
    "compensation": "$124,000 - $241,500"
  },
  {
    "id": "optiver-8405271002",
    "company": "Optiver",
    "title": "Machine Learning Performance Engineer",
    "location": "New York, NY, United States",
    "source": "Official Careers",
    "url": "https://www.optiver.com/join-us/jobs/technology/new-york/machine-learning-performance-engineer/?gh_jid=8405271002",
    "score": 17,
    "tracks": [
      "systems-performance",
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 提到 distributed training",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "jane-street-7449077002",
    "company": "Jane Street",
    "title": "Machine Learning Performance Engineer",
    "location": "New York, New York, United States",
    "source": "Greenhouse",
    "url": "https://www.janestreet.com/join-jane-street/apply/7449077002?gh_jid=7449077002",
    "score": 14,
    "tracks": [
      "systems-performance",
      "kernel-accelerator",
      "training-infra"
    ],
    "reasons": [
      "岗位以系统性能工程为核心",
      "JD 涉及底层训练栈",
      "JD 涉及大规模训练"
    ]
  },
  {
    "id": "jane-street-6485460002",
    "company": "Jane Street",
    "title": "Machine Learning Research Engineer",
    "location": "New York, New York, United States",
    "source": "Greenhouse",
    "url": "https://www.janestreet.com/join-jane-street/apply/6485460002?gh_jid=6485460002",
    "score": 9,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "人工审核确认岗位包含 training infrastructure 工作"
    ]
  },
  {
    "id": "hrt-7972584",
    "company": "HRT",
    "title": "AI Research Engineer, Pre-Training",
    "location": "New York, NY, United States",
    "source": "Official Careers",
    "url": "https://www.hudsonrivertrading.com/careers/job/?gh_jid=7972584",
    "score": 22,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 pretraining",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "de-shaw-4954",
    "company": "D. E. Shaw",
    "title": "Machine Learning Researcher",
    "location": "New York, NY, United States",
    "source": "Official Careers",
    "url": "https://www.deshaw.com/careers/machine-learning-researcher-4954",
    "score": 12,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "ML researcher 岗位明确包含底层训练系统工作",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "meta-3414246448833665",
    "company": "Meta",
    "title": "Software Engineer, Systems ML",
    "location": "Sunnyvale, CA, United States · Bellevue, WA, United States · Menlo Park, CA, United States · Remote, US · New York, NY, United States",
    "source": "Official Careers",
    "url": "https://www.metacareers.com/profile/job_details/3414246448833665/",
    "score": 11,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "标题明确包含 ML systems"
    ]
  },
  {
    "id": "meta-2236774387100356",
    "company": "Meta",
    "title": "AI Software Engineer, Systems ML - Wearables AI",
    "location": "Seattle, WA, United States",
    "source": "Official Careers",
    "url": "https://www.metacareers.com/profile/job_details/2236774387100356/",
    "score": 11,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "标题明确包含 ML systems"
    ]
  },
  {
    "id": "radixark-449f4bc0-6cc2-4164-9111-522d77fded43",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Developer Experience",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/449f4bc0-6cc2-4164-9111-522d77fded43",
    "score": 16,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "radixark-e610fbb8-3ba8-416e-b193-13ee5d156f34",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Developer Technology",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/e610fbb8-3ba8-416e-b193-13ee5d156f34",
    "score": 28,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "radixark-134eea08-4726-46e1-a0e7-7c1dfc9545cd",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Inference-Core Engine",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/134eea08-4726-46e1-a0e7-7c1dfc9545cd",
    "score": 21,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "radixark-3cf5c262-a47c-4de4-a6fd-3baa1747f1c4",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Inference-Kernel, Compiler & Communication",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/3cf5c262-a47c-4de4-a6fd-3baa1747f1c4",
    "score": 25,
    "tracks": [
      "training-infra",
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及 collective communication"
    ]
  },
  {
    "id": "radixark-0c73a420-3ee0-4b63-9bd5-0a9266d8a727",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Inference-Multi-Hardware",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/0c73a420-3ee0-4b63-9bd5-0a9266d8a727",
    "score": 23,
    "tracks": [
      "training-infra",
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及 collective communication"
    ]
  },
  {
    "id": "radixark-41974f86-20b6-4508-a290-a17e079353bc",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Inference-Multimodal & Diffusion",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/41974f86-20b6-4508-a290-a17e079353bc",
    "score": 13,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及训练 pipeline"
    ]
  },
  {
    "id": "radixark-dd738532-223c-4b00-9536-a3a635d332a1",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Inference-TPU",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/dd738532-223c-4b00-9536-a3a635d332a1",
    "score": 32,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "radixark-0a365274-a3e7-4850-ac52-f0c40c3185d0",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Performance",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/0a365274-a3e7-4850-ac52-f0c40c3185d0",
    "score": 18,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "radixark-9fbc7dd7-bbfd-49f7-ab03-138aa5db8ece",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Product",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/9fbc7dd7-bbfd-49f7-ab03-138aa5db8ece",
    "score": 18,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "radixark-1dc7196e-8605-462e-a9b9-23ada702c3e6",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Reliability-CI Infrastructure",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/1dc7196e-8605-462e-a9b9-23ada702c3e6",
    "score": 16,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "radixark-ba198727-37e6-4062-b93d-3431dd26f7dc",
    "company": "RadixArk",
    "title": "Member of Technical Staff — Training",
    "location": "Palo Alto Office",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/radixark/ba198727-37e6-4062-b93d-3431dd26f7dc",
    "score": 33,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 提到 training framework"
    ]
  },
  {
    "id": "inferact-24ea1266-bc29-4838-9a61-8adc1d5bb2c6",
    "company": "Inferact",
    "title": "Member of Technical Staff, TPU Performance Engineering",
    "location": "San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/inferact/24ea1266-bc29-4838-9a61-8adc1d5bb2c6",
    "score": 18,
    "tracks": [
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 TPU performance",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "$200K - $400K"
  },
  {
    "id": "cohere-3136a5a5-06fd-4c82-8b72-a43467e6b128",
    "company": "Cohere",
    "title": "Member of Technical Staff, Modeling",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/3136a5a5-06fd-4c82-8b72-a43467e6b128",
    "score": 11,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-d42f5fd4-1ffc-45b9-957c-f09862db6af6",
    "company": "Cohere",
    "title": "Member of Technical Staff, Training Performance Engineer",
    "location": "New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/d42f5fd4-1ffc-45b9-957c-f09862db6af6",
    "score": 31,
    "tracks": [
      "systems-performance",
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training performance",
      "岗位以系统性能工程为核心",
      "JD 提到 distributed training"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-a13207e7-dc82-473f-8ca4-e832452fe8c3",
    "company": "Cohere",
    "title": "Member of Technical Staff, Training Infra Engineer",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/a13207e7-dc82-473f-8ca4-e832452fe8c3",
    "score": 31,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training infrastructure",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-554a9380-ab50-4338-88a9-c6b8ab19d92e",
    "company": "Cohere",
    "title": "Member of Technical Staff, Post-Training",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/554a9380-ab50-4338-88a9-c6b8ab19d92e",
    "score": 21,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 post-training",
      "JD 提到 distributed training",
      "JD 提到 SFT / fine-tuning infrastructure"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-859e2e47-02fb-4afe-bb8a-e83bf4d8c265",
    "company": "Cohere",
    "title": "Member of Technical Staff, Pre-Training Data",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/859e2e47-02fb-4afe-bb8a-e83bf4d8c265",
    "score": 11,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 pretraining",
      "JD 关注训练吞吐或利用率"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-e9ef9420-88e5-403b-82e8-1c36fa010d4d",
    "company": "Cohere",
    "title": "Member of Technical Staff, Integration/RL Team (Research Engineer)",
    "location": "New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/e9ef9420-88e5-403b-82e8-1c36fa010d4d",
    "score": 16,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 SFT / fine-tuning infrastructure",
      "JD 涉及底层训练栈"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-c99e61c9-ed92-426d-9711-188dfc0f729f",
    "company": "Cohere",
    "title": "Senior ML Systems Engineer, Frameworks & Tooling",
    "location": "San Francisco · New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/c99e61c9-ed92-426d-9711-188dfc0f729f",
    "score": 31,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 ML systems",
      "JD 提到 distributed training",
      "JD 提到 training framework"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "cohere-8878b0d0-7d88-4ee9-bc17-b0dd237e39a0",
    "company": "Cohere",
    "title": "Member of Technical Staff, Agentic Environments",
    "location": "New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/cohere/8878b0d0-7d88-4ee9-bc17-b0dd237e39a0",
    "score": 11,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ],
    "compensation": "CA$250K - CA$535K"
  },
  {
    "id": "together-ai-5131941007",
    "company": "Together AI",
    "title": "Forward Deployed Engineer (Inference & Post-Training)",
    "location": "San Francisco",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/togetherai/jobs/5131941007",
    "score": 17,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 post-training",
      "JD 提到 SFT / fine-tuning infrastructure",
      "JD 涉及训练 pipeline"
    ]
  },
  {
    "id": "together-ai-5199554007",
    "company": "Together AI",
    "title": "Research Engineer, Large-Scale Training",
    "location": "San Francisco",
    "source": "Greenhouse",
    "url": "https://job-boards.greenhouse.io/togetherai/jobs/5199554007",
    "score": 26,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 提到 training framework"
    ]
  },
  {
    "id": "fireworks-ai-a2850702-dea3-4e2c-a3ec-7ae257d36eb7",
    "company": "Fireworks AI",
    "title": "Member of Technical Staff, AI Training Infrastructure",
    "location": "Greater Seattle Area · New York · San Francisco",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/fireworks/a2850702-dea3-4e2c-a3ec-7ae257d36eb7",
    "score": 30,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 training infrastructure",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ],
    "compensation": "$210K - $320K"
  },
  {
    "id": "fireworks-ai-ad58a098-ef75-4a4b-8475-55c2653213ef",
    "company": "Fireworks AI",
    "title": "Member of Technical Staff, Systems Infrastructure (2026 PhD New Grad)",
    "location": "New York",
    "source": "Ashby",
    "url": "https://jobs.ashbyhq.com/fireworks/ad58a098-ef75-4a4b-8475-55c2653213ef",
    "score": 12,
    "tracks": [
      "systems-performance",
      "kernel-accelerator",
      "training-infra"
    ],
    "reasons": [
      "JD 涉及 collective communication",
      "JD 涉及底层训练栈",
      "JD 涉及大规模训练"
    ],
    "compensation": "$200K - $230K"
  },
  {
    "id": "amazon-10538219",
    "company": "Amazon",
    "title": "CPLD/FPGA Firmware Engineer, Annapurna Labs, ML Accelerator Systems Firmware",
    "location": "Austin, Texas, USA · US, TX, Austin",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10538219/cpld-fpga-firmware-engineer-annapurna-labs-ml-accelerator-systems-firmware",
    "score": 10,
    "tracks": [
      "kernel-accelerator"
    ],
    "reasons": [
      "岗位聚焦 AI accelerator"
    ]
  },
  {
    "id": "amazon-10556984",
    "company": "Amazon",
    "title": "Machine Learning Engineer, Advertising & Marketing Performance Intelligence",
    "location": "Seattle, Washington, USA · US, WA, Seattle",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10556984/machine-learning-engineer-advertising-marketing-performance-intelligence",
    "score": 14,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及 learning infrastructure",
      "JD 涉及训练 pipeline"
    ]
  },
  {
    "id": "amazon-10434988",
    "company": "Amazon",
    "title": "ML Accelerator Performance Validation Engineer, Post Silicon Validation",
    "location": "Austin, Texas, USA · US, TX, Austin",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10434988/ml-accelerator-performance-validation-engineer-post-silicon-validation",
    "score": 19,
    "tracks": [
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 AI accelerator",
      "JD 涉及 collective communication",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "amazon-10421819",
    "company": "Amazon",
    "title": "ML Infrastructure Engineer, Fauna",
    "location": "New York, New York, USA · US, NY, New York",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10421819/ml-infrastructure-engineer-fauna",
    "score": 15,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "标题提到 ML infrastructure",
      "JD 提到 training infrastructure",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "amazon-10388015",
    "company": "Amazon",
    "title": "Neuron Runtime Software Development Engineer , Neuron Runtime",
    "location": "Seattle, Washington, USA · US, WA, Seattle",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10388015/neuron-runtime-software-development-engineer-neuron-runtime",
    "score": 11,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "amazon-10473201",
    "company": "Amazon",
    "title": "Neuron Runtime Software Development Engineer , Neuron Runtime",
    "location": "Seattle, Washington, USA · Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10473201/neuron-runtime-software-development-engineer-neuron-runtime",
    "score": 11,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及底层训练栈",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "amazon-10375239",
    "company": "Amazon",
    "title": "Senior SoC Systems Software Engineer, Annapurna Labs Machine Learning Accelerators, AWS",
    "location": "Austin, Texas, USA · Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10375239/senior-soc-systems-software-engineer-annapurna-labs-machine-learning-accelerators-aws",
    "score": 30,
    "tracks": [
      "kernel-accelerator",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 AI accelerator",
      "JD 涉及 ML framework internals",
      "JD 涉及 collective communication"
    ]
  },
  {
    "id": "amazon-10378122",
    "company": "Amazon",
    "title": "SoC Systems Software Engineer, Annapurna Labs Machine Learning Accelerators, AWS",
    "location": "Austin, Texas, USA · Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10378122/soc-systems-software-engineer-annapurna-labs-machine-learning-accelerators-aws",
    "score": 30,
    "tracks": [
      "kernel-accelerator",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "岗位聚焦 AI accelerator",
      "JD 涉及 ML framework internals",
      "JD 涉及 collective communication"
    ]
  },
  {
    "id": "amazon-10444927",
    "company": "Amazon",
    "title": "Software Dev Engineer II, Stores Foundational AI -SFAI",
    "location": "Seattle, Washington, USA · US, WA, Seattle",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10444927/software-dev-engineer-ii-stores-foundational-ai-sfai",
    "score": 18,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 SFT / fine-tuning infrastructure",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "amazon-10490741",
    "company": "Amazon",
    "title": "Software Development Engineer I – AI/ML Network Infrastructure, Annapurna Labs",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10490741/software-development-engineer-i-ai-ml-network-infrastructure-annapurna-labs",
    "score": 11,
    "tracks": [
      "training-infra",
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 涉及 learning infrastructure",
      "JD 涉及 collective communication",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "amazon-10492391",
    "company": "Amazon",
    "title": "Software Development Engineer II, AWS SageMaker AI",
    "location": "Bellevue, Washington, USA · US, WA, Bellevue",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10492391/software-development-engineer-ii-aws-sagemaker-ai",
    "score": 15,
    "tracks": [
      "training-infra",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 涉及大规模训练"
    ]
  },
  {
    "id": "amazon-10492392",
    "company": "Amazon",
    "title": "Software Development Engineer II, AWS SageMaker AI",
    "location": "Bellevue, Washington, USA · US, WA, Bellevue",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10492392/software-development-engineer-ii-aws-sagemaker-ai",
    "score": 15,
    "tracks": [
      "training-infra",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 涉及大规模训练"
    ]
  },
  {
    "id": "amazon-10488707",
    "company": "Amazon",
    "title": "Software Development Engineer, ML Systems, Annapurna Labs",
    "location": "New York, New York, USA · US, NY, New York",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10488707/software-development-engineer-ml-systems-annapurna-labs",
    "score": 14,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 ML systems",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "amazon-3062273",
    "company": "Amazon",
    "title": "Software Development Engineer, ML Systems, Annapurna Labs",
    "location": "New York, New York, USA · US, NY, New York",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/3062273/software-development-engineer-ml-systems-annapurna-labs",
    "score": 14,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 ML systems",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "amazon-10501454",
    "company": "Amazon",
    "title": "Software Engineer- AI/ML, Amazon Neuron Training",
    "location": "Seattle, Washington, USA · Cupertino, California, USA · US, WA, Seattle",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10501454/software-engineer-ai-ml-amazon-neuron-training",
    "score": 19,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 涉及 ML accelerator",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "amazon-10555767",
    "company": "Amazon",
    "title": "Software Engineer- AI/ML, Amazon Neuron Training",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10555767/software-engineer-ai-ml-amazon-neuron-training",
    "score": 32,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "amazon-3175270",
    "company": "Amazon",
    "title": "Software Engineer- AI/ML, AWS Neuron Distributed Training - Performance Optimization",
    "location": "Seattle, Washington, USA · Cupertino, California, USA · US, WA, Seattle",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/3175270/software-engineer-ai-ml-aws-neuron-distributed-training-performance-optimization",
    "score": 36,
    "tracks": [
      "systems-performance",
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training performance",
      "标题明确包含 distributed training",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "amazon-10433217",
    "company": "Amazon",
    "title": "Sr Software Development Engineer, Neuron Collectives, Annapurna Labs",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10433217/sr-software-development-engineer-neuron-collectives-annapurna-labs",
    "score": 16,
    "tracks": [
      "training-infra",
      "ml-framework",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 涉及 collective communication"
    ]
  },
  {
    "id": "amazon-10555762",
    "company": "Amazon",
    "title": "Sr. Software Engineer- AI/ML, Amazon Neuron Training",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10555762/sr-software-engineer-ai-ml-amazon-neuron-training",
    "score": 32,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "amazon-10497224",
    "company": "Amazon",
    "title": "Sr. Software Engineer- AI/ML, AWS Neuron Distributed Training",
    "location": "Seattle, Washington, USA · Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10497224/sr-software-engineer-ai-ml-aws-neuron-distributed-training",
    "score": 30,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 distributed training",
      "JD 提到 distributed training",
      "JD 涉及 ML accelerator"
    ]
  },
  {
    "id": "amazon-10515931",
    "company": "Amazon",
    "title": "Sr. Software Engineer- AI/ML, AWS Neuron Distributed Training",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10515931/sr-software-engineer-ai-ml-aws-neuron-distributed-training",
    "score": 22,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 distributed training",
      "JD 提到 distributed training",
      "JD 涉及底层训练栈"
    ]
  },
  {
    "id": "amazon-10556379",
    "company": "Amazon",
    "title": "Sr. Software Engineer- AI/ML, AWS Neuron Distributed Training",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10556379/sr-software-engineer-ai-ml-aws-neuron-distributed-training",
    "score": 30,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 distributed training",
      "JD 提到 distributed training",
      "JD 涉及 ML accelerator"
    ]
  },
  {
    "id": "amazon-3168219",
    "company": "Amazon",
    "title": "Sr. Software Engineer- AI/ML, AWS Neuron Distributed Training",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/3168219/sr-software-engineer-ai-ml-aws-neuron-distributed-training",
    "score": 32,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "标题明确包含 distributed training",
      "JD 提到 distributed training",
      "JD 提到 training framework"
    ]
  },
  {
    "id": "amazon-2989101",
    "company": "Amazon",
    "title": "Sr. Software Engineer- AI/ML, AWS Neuron Distributed Training - Performance Optimization",
    "location": "Seattle, Washington, USA · US, WA, Seattle",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/2989101/sr-software-engineer-ai-ml-aws-neuron-distributed-training-performance-optimization",
    "score": 36,
    "tracks": [
      "systems-performance",
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training performance",
      "标题明确包含 distributed training",
      "JD 提到 distributed training"
    ]
  },
  {
    "id": "amazon-10558915",
    "company": "Amazon",
    "title": "Software Development Engineer I, Annapurna Labs, Early Career - 2027",
    "location": "Austin, Texas, USA · Seattle, Washington, USA · New York, New York, USA · Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10558915/software-development-engineer-i-annapurna-labs-early-career-2027",
    "score": 13,
    "tracks": [
      "training-infra",
      "kernel-accelerator"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 涉及 compiler / MLIR 优化"
    ]
  },
  {
    "id": "amazon-10565690",
    "company": "Amazon",
    "title": "Machine Learning Engineer, Sequence Models (project Sequoia)",
    "location": "New York, New York, USA · US, NY, New York",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10565690/machine-learning-engineer-sequence-models-project-sequoia",
    "score": 12,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联",
      "JD 关注训练吞吐或利用率"
    ]
  },
  {
    "id": "amazon-10570613",
    "company": "Amazon",
    "title": "Software Engineer- AI/ML, Amazon Neuron Training",
    "location": "Cupertino, California, USA · US, CA, Cupertino",
    "source": "Amazon Jobs",
    "url": "https://www.amazon.jobs/en/jobs/10570613/software-engineer-ai-ml-amazon-neuron-training",
    "score": 32,
    "tracks": [
      "training-infra",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 training infrastructure",
      "JD 提到 distributed training",
      "JD 将 distributed training 与 infrastructure 直接关联"
    ]
  },
  {
    "id": "microsoft-ai-200009146",
    "company": "Microsoft AI",
    "title": "Pre-Training Infrastructure",
    "location": "Mountain View, California, United States",
    "source": "Microsoft AI Careers",
    "url": "https://microsoft.ai/careers/job/4410382009/pre-training-infrastructure/",
    "score": 47,
    "tracks": [
      "training-infra",
      "systems-performance",
      "kernel-accelerator"
    ],
    "reasons": [
      "标题明确包含 training infrastructure",
      "岗位聚焦 pretraining",
      "JD 提到 training infrastructure"
    ],
    "compensation": "$142,800 - $304,200"
  },
  {
    "id": "microsoft-ai-200054206",
    "company": "Microsoft AI",
    "title": "Pre-Training",
    "location": "Mountain View, California, United States",
    "source": "Microsoft AI Careers",
    "url": "https://microsoft.ai/careers/job/4404559009/pre-training/",
    "score": 12,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 pretraining",
      "JD 涉及大规模训练"
    ],
    "compensation": "$119,800 - $304,200"
  },
  {
    "id": "microsoft-ai-200057458",
    "company": "Microsoft AI",
    "title": "Software Engineer, Reinforcement Learning",
    "location": "Mountain View, New York City, Redmond, California, New York, Washington, United States",
    "source": "Microsoft AI Careers",
    "url": "https://microsoft.ai/careers/job/4418869009/software-engineer-reinforcement-learning/",
    "score": 18,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 SFT / fine-tuning infrastructure",
      "JD 涉及大规模训练"
    ],
    "compensation": "$142,800 - $304,200"
  },
  {
    "id": "microsoft-ai-200058879",
    "company": "Microsoft AI",
    "title": "AI Evaluation Systems Engineering Lead",
    "location": "Mountain View, California, United States",
    "source": "Microsoft AI Careers",
    "url": "https://microsoft.ai/careers/job/4425409009/ai-evaluation-systems-engineering-lead/",
    "score": 17,
    "tracks": [
      "training-infra",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 明确属于 RL training infrastructure",
      "JD 涉及 learning infrastructure"
    ],
    "compensation": "$142,800 - $331,200"
  },
  {
    "id": "microsoft-ai-200059719",
    "company": "Microsoft AI",
    "title": "Safety Post-training",
    "location": "London, Mountain View, New York City, Zurich, California, New York, United Kingdom, United States, Switzerland",
    "source": "Microsoft AI Careers",
    "url": "https://microsoft.ai/careers/job/4430492009/safety-post-training/",
    "score": 20,
    "tracks": [
      "training-infra"
    ],
    "reasons": [
      "岗位聚焦 post-training",
      "JD 提到 distributed training",
      "JD 明确属于 RL training infrastructure"
    ],
    "compensation": "$119,800 - $261,000"
  },
  {
    "id": "microsoft-ai-200059285",
    "company": "Microsoft AI",
    "title": "Senior Network Production Engineer, AI Supercomputing",
    "location": "Mountain View, California, United States",
    "source": "Microsoft AI Careers",
    "url": "https://microsoft.ai/careers/job/4432950009/senior-network-production-engineer-ai-supercomputing/",
    "score": 15,
    "tracks": [
      "training-infra",
      "ml-framework",
      "kernel-accelerator",
      "systems-performance"
    ],
    "reasons": [
      "JD 提到 distributed training",
      "JD 提到 training framework",
      "JD 涉及底层训练栈"
    ],
    "compensation": "$119,800 - $304,200"
  }
];

export const companyCounts = jobs.reduce<Record<Company, number>>(
  (counts, job) => ({ ...counts, [job.company]: counts[job.company] + 1 }),
  {"OpenAI": 0, "Anthropic": 0, "SpaceXAI": 0, "Cursor": 0, "Google DeepMind": 0, "Google": 0, "MAI Superintelligence": 0, "Thinking Machines Lab": 0, "Periodic Labs": 0, "NVIDIA": 0, "Optiver": 0, "Jane Street": 0, "HRT": 0, "D. E. Shaw": 0, "Citadel": 0, "Meta": 0, "RadixArk": 0, "Inferact": 0, "Cohere": 0, "Together AI": 0, "Fireworks AI": 0, "Apple": 0, "Amazon": 0, "Microsoft AI": 0},
);
