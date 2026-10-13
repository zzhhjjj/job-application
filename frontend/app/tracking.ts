import type { Company, Job } from "./jobs";

export const stageLabels = {
  pending: "待看",
  interested: "感兴趣",
  applied: "已投递",
  ignored: "不感兴趣",
} as const;

export const availabilityLabels = {
  active: "当前匹配",
  unverified: "尚未重新验证",
  not_seen: "本次未发现",
  no_match: "不再符合筛选",
  closed: "已确认下架",
} as const;

export const eventLabels: Record<string, string> = {
  new: "新增入选",
  updated: "职位内容变更",
  returned: "重新入选",
  verified: "重新确认有效",
  not_seen: "本次未发现",
  no_match: "不再符合筛选",
  closed: "已确认下架",
};

export type Personal = {
  favorite: boolean;
  stage: keyof typeof stageLabels;
  notes: string;
  revision: number;
};

export type PersonalFilter =
  | keyof typeof stageLabels
  | "all"
  | "favorites"
  | "hide-applied"
  | "including-ignored";

export function matchesPersonalFilter(personal: Personal | undefined, filter: PersonalFilter) {
  const stage = personal?.stage ?? "pending";

  if (filter === "all") return stage !== "ignored";
  if (filter === "hide-applied") return stage !== "ignored" && stage !== "applied";
  if (filter === "favorites") return Boolean(personal?.favorite);
  if (filter === "including-ignored") return true;
  return stage === filter;
}

export type TrackedJob = Job & {
  availability?: keyof typeof availabilityLabels;
  firstSeenAt?: string;
  lastSeenAt?: string;
  baseline?: boolean;
  additionGroup?: "latest" | "earlier" | null;
  unread?: string[];
  personal?: Personal;
};

export type SourceHealth = {
  company: string;
  status: "never" | "running" | "ok" | "partial" | "failed";
  coverage: string;
  lastAttempt: string | null;
  lastSuccess: string | null;
  error: string | null;
  discoveredCount: number;
  matchedCount: number;
};

export type RadarData = {
  companyTiers?: Partial<Record<Company, 1 | 2>>;
  jobs: TrackedJob[];
  sources: SourceHealth[];
  latestEventId: number;
  reviewedEventId: number;
  refreshing: boolean;
  refreshError?: string | null;
  latestBatch?: {
    id: number;
    startedAt: string;
    completedAt: string | null;
    status: "running" | "complete" | "partial" | "interrupted";
  } | null;
};

export type JobEvent = {
  id: number;
  kind: string;
  occurredAt: string;
  changes: Record<string, { before: unknown; after: unknown }>;
};

export function dateLabel(value?: string | null) {
  return value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "尚无记录";
}

export async function radarRequest<T>(path = "", body?: object): Promise<T> {
  const response = await fetch(`/api/radar${path}`, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
    signal: AbortSignal.timeout(15000),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(data?.error ?? "本地岗位服务暂不可用，请重试");
  return data as T;
}

export const jobViewLabels = {
  all: "全部岗位",
  latest: "本次新增",
  earlier: "此前新增待投",
} as const;

export type JobView = keyof typeof jobViewLabels;

export function matchesJobView(job: TrackedJob, view: JobView) {
  if (view === "all") return true;
  return job.additionGroup === view
    && ["active", "unverified"].includes(job.availability ?? "active")
    && matchesPersonalFilter(job.personal, "hide-applied");
}
