import type { Company, MatchTrack } from "./jobs";

export const companies: readonly Company[] = [
  "Amazon",
  "Anthropic",
  "Apple",
  "Citadel",
  "Cohere",
  "Cursor",
  "D. E. Shaw",
  "Fireworks AI",
  "Google",
  "Google DeepMind",
  "HRT",
  "Inferact",
  "Jane Street",
  "MAI Superintelligence",
  "Meta",
  "Microsoft AI",
  "NVIDIA",
  "OpenAI",
  "Optiver",
  "Periodic Labs",
  "RadixArk",
  "SpaceXAI",
  "Thinking Machines Lab",
  "Together AI"
];

export const companyMeta: Record<
  Company,
  { monogram: string; slug: string }
> = {
  OpenAI: { monogram: "O", slug: "openai" },
  Anthropic: { monogram: "A", slug: "anthropic" },
  SpaceXAI: { monogram: "X", slug: "spacexai" },
  Cursor: { monogram: "C", slug: "cursor" },
  "Google DeepMind": { monogram: "G", slug: "deepmind" },
  Google: { monogram: "G", slug: "google" },
  "MAI Superintelligence": { monogram: "S", slug: "mai-superintelligence" },
  "Thinking Machines Lab": { monogram: "T", slug: "thinking-machines" },
  "Periodic Labs": { monogram: "P", slug: "periodic-labs" },
  NVIDIA: { monogram: "N", slug: "nvidia" },
  Optiver: { monogram: "O", slug: "optiver" },
  "Jane Street": { monogram: "J", slug: "jane-street" },
  HRT: { monogram: "H", slug: "hrt" },
  "D. E. Shaw": { monogram: "D", slug: "de-shaw" },
  Citadel: { monogram: "C", slug: "citadel" },
  Meta: { monogram: "M", slug: "meta" },
  RadixArk: { monogram: "R", slug: "radixark" },
  Inferact: { monogram: "I", slug: "inferact" },
  Cohere: { monogram: "C", slug: "cohere" },
  "Together AI": { monogram: "T", slug: "together-ai" },
  "Fireworks AI": { monogram: "F", slug: "fireworks-ai" },
  Apple: { monogram: "A", slug: "apple" },
  Amazon: { monogram: "A", slug: "amazon" },
  "Microsoft AI": { monogram: "M", slug: "microsoft-ai" },
};

export const trackLabels: Record<MatchTrack, string> = {
  "training-infra": "Training infra",
  "systems-performance": "Systems performance",
  "kernel-accelerator": "Kernel / accelerator",
  "ml-framework": "ML framework",
};

export const locationOptions = [
  { value: "all", label: "全部地点" },
  { value: "san francisco", label: "San Francisco" },
  { value: "new york", label: "New York" },
  { value: "mountain view", label: "Mountain View" },
  { value: "seattle", label: "Seattle" },
  { value: "remote", label: "Remote-friendly" },
  { value: "santa clara", label: "Santa Clara" },
  { value: "austin", label: "Austin" },
] as const;

export const sortOptions = [
  { value: "newest", label: "按首次入选" },
  { value: "fit", label: "按匹配度" },
  { value: "company", label: "按公司" },
  { value: "title", label: "按职位名" },
  { value: "location", label: "按地点" },
] as const;
