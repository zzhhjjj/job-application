"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  companies,
  companyMeta,
  locationOptions,
  sortOptions,
  trackLabels,
} from "./ui-config";
import { jobs as snapshotJobs, snapshotDate, type Company, type Job } from "./jobs";
import { JobActions } from "./JobActions";
import { SourceStatus } from "./SourceStatus";
import {
  availabilityLabels,
  dateLabel,
  jobViewLabels,
  matchesJobView,
  matchesPersonalFilter,
  radarRequest,
  stageLabels,
  type Personal,
  type PersonalFilter,
  type RadarData,
  type TrackedJob,
  type JobView,
} from "./tracking";

type CompanyFilter = "全部公司" | Company;
type SortKey = (typeof sortOptions)[number]["value"];

const emptyCompanyTiers: Partial<Record<Company, 1 | 2>> = {};

const defaultPersonalFilter: PersonalFilter = "hide-applied";

const collator = new Intl.Collator("en", { sensitivity: "base" });

function matchesLocation(job: Job, location: string) {
  if (location === "all") return true;
  return job.location.toLocaleLowerCase().includes(location.toLocaleLowerCase());
}

function JobCard({ job, index, ready, onSave, sourceFailed, localTier }: {
  localTier?: 1 | 2;
  job: TrackedJob; index: number; ready: boolean; sourceFailed: boolean;
  onSave: (job: TrackedJob, patch: Partial<Personal>) => Promise<void>;
}) {
  const meta = companyMeta[job.company];
  const historical = job.availability && !["active", "unverified"].includes(job.availability);
  const priority = historical ? "上次入选评分" : job.score >= 15 ? "核心匹配" : "相关机会";

  return (
    <article
      className={`job-card company-${meta.slug}`}
      style={{ "--card-index": index } as React.CSSProperties}
      data-company={job.company}
      data-testid="job-card"
    >
      <div className="job-card__topline">
        <div className="company-label">
          <span className="company-mark" aria-hidden="true">
            {meta.monogram}
          </span>
          <span>{job.company}</span>
          {localTier && <span className="tier-badge" title="本地偏好">T{localTier}</span>}
        </div>
        <span className="source-label">via {job.source}</span>
      </div>

      <h3>{job.title}</h3>
      {job.additionGroup && <p className="addition-meta">
        <span className="addition-badge">{job.additionGroup === "latest" ? "本次新增" : "此前新增"}</span>
        {job.firstSeenAt && <time dateTime={job.firstSeenAt}>
          {new Date(job.firstSeenAt).toLocaleDateString("zh-CN")} 收录
        </time>}
      </p>}
      {sourceFailed && <p className="service-message">来源刷新失败，当前保留上次获取的岗位信息。</p>}

      <div className="match-summary">
        <span className={job.score >= 15 ? "fit-badge is-core" : "fit-badge"}>
          {priority} · 规则分 {job.score}
        </span>
        <div className="track-list" aria-label="匹配方向">
          {job.tracks.map((track) => (
            <span key={track}>{trackLabels[track]}</span>
          ))}
        </div>
      </div>

      <p className="match-reason">{job.reasons.join(" · ")}</p>

      <div className="job-card__details">
        <p className="location-line">
          <span className="location-pin" aria-hidden="true" />
          {job.location}
        </p>
        {job.compensation ? (
          <p className="compensation-line">{job.compensation}</p>
        ) : (
          <p className="compensation-line compensation-line--muted">薪资见详情</p>
        )}
      </div>

      <a className="job-link" href={job.url} target="_blank" rel="noreferrer">
        查看职位
        <span aria-hidden="true">↗</span>
      </a>
      <JobActions job={job} ready={ready} onSave={onSave} />
    </article>
  );
}

export function JobsDashboard() {
  const [radar, setRadar] = useState<RadarData | null>(null);
  const [ready, setReady] = useState(false);
  const [serviceError, setServiceError] = useState("");
  const [actionError, setActionError] = useState("");
  const [actionBusy, setActionBusy] = useState(false);
  const requestSequence = useRef(0);
  const [changes, setChanges] = useState("all");
  const [personalFilter, setPersonalFilter] = useState<PersonalFilter>(defaultPersonalFilter);
  const [availability, setAvailability] = useState("current");
  const [company, setCompany] = useState<CompanyFilter>("全部公司");
  const [tierFilter, setTierFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("all");
  const [sort, setSort] = useState<SortKey>("fit");
  const [jobView, setJobView] = useState<JobView>("all");

  const load = useCallback(async () => {
    const sequence = ++requestSequence.current;
    try {
      const data = await radarRequest<RadarData>();
      if (sequence !== requestSequence.current) return;
      setRadar((previous) => {
        const saved = new Map(previous?.jobs.map((job) => [job.id, job.personal]));
        return { ...data, jobs: data.jobs.map((job) => {
          const personal = saved.get(job.id);
          return personal && personal.revision > (job.personal?.revision ?? -1) ? { ...job, personal } : job;
        }) };
      });
      setReady(true);
      setServiceError("");
    } catch {
      if (sequence !== requestSequence.current) return;
      setReady(false);
      setServiceError("本地岗位服务暂不可用。当前为只读缓存，无法保存个人状态或确认岗位新鲜度。");
    }
  }, []);

  useEffect(() => {
    const initial = setTimeout(() => void load(), 0);
    const timer = setInterval(() => void load(), 10000);
    const onFocus = () => void load();
    window.addEventListener("focus", onFocus);
    return () => { clearTimeout(initial); clearInterval(timer); window.removeEventListener("focus", onFocus); };
  }, [load]);

  async function savePersonal(job: TrackedJob, patch: Partial<Personal>) {
    try {
      const personal = await radarRequest<Personal>(`/jobs/${job.id}`, { ...patch, revision: job.personal?.revision });
      setRadar((previous) => previous ? { ...previous, jobs: previous.jobs.map((item) => item.id === job.id ? { ...item, personal } : item) } : previous);
    } catch (error) {
      await load();
      throw error;
    }
  }

  async function runAction(action: "refresh" | "reviewed") {
    setActionBusy(true);
    setActionError("");
    try {
      await radarRequest(`/${action}`, action === "reviewed" ? { eventId: radar?.latestEventId ?? 0 } : {});
      await load();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "操作失败，请重试");
    } finally { setActionBusy(false); }
  }

  const jobs: readonly TrackedJob[] = radar?.jobs ?? snapshotJobs;
  const companyTiers = radar?.companyTiers ?? emptyCompanyTiers;
  const hasLocalTiers = Object.keys(companyTiers).length > 0;
  const currentJobs = jobs.filter((job) => !job.availability || ["active", "unverified"].includes(job.availability));
  const unreadNew = jobs.filter((job) => job.unread?.includes("new")).length;
  const unreadChanges = jobs.filter((job) => job.unread?.some((kind) => kind !== "new")).length;

  const scopeJobs = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    return jobs.filter((job) => {
      const searchable = `${job.title} ${job.company} ${job.location} ${job.tracks
        .map((track) => trackLabels[track])
        .join(" ")} ${job.reasons.join(" ")}`.toLocaleLowerCase();
      const matchesQuery = !normalizedQuery || searchable.includes(normalizedQuery);
      return matchesQuery && matchesLocation(job, location)
        && (!hasLocalTiers || tierFilter === "all" || String(companyTiers[job.company] ?? "unassigned") === tierFilter);
    });
  }, [jobs, location, query, hasLocalTiers, tierFilter, companyTiers]);

  const jobsMatchingSharedFilters = useMemo(() => {
    return scopeJobs.filter((job) => {
      if (jobView !== "all") return matchesJobView(job, jobView);
      const lifecycle = job.availability ?? "active";
      const matchesAvailability = availability === "all" || (availability === "current" ? ["active", "unverified"].includes(lifecycle) : lifecycle === availability);
      const matchesChanges = changes === "all" || (changes === "new" ? job.unread?.includes("new") : job.unread?.some((kind) => kind !== "new"));
      return matchesAvailability
        && matchesChanges
        && matchesPersonalFilter(job.personal, personalFilter);
    });
  }, [scopeJobs, jobView, availability, changes, personalFilter]);

  const companyScopeJobs = scopeJobs.filter((job) => company === "全部公司" || job.company === company);
  const viewCounts = {
    latest: companyScopeJobs.filter((job) => matchesJobView(job, "latest")).length,
    earlier: companyScopeJobs.filter((job) => matchesJobView(job, "earlier")).length,
  };
  const latestAdditionCount = companyScopeJobs.filter((job) => job.additionGroup === "latest").length;

  const filteredCompanyCounts = useMemo(
    () =>
      jobsMatchingSharedFilters.reduce<Record<Company, number>>(
        (counts, job) => ({ ...counts, [job.company]: counts[job.company] + 1 }),
        Object.fromEntries(companies.map((name) => [name, 0])) as Record<Company, number>,
      ),
    [jobsMatchingSharedFilters],
  );

  const visibleJobs = useMemo(() => {
    const filtered = jobsMatchingSharedFilters.filter(
      (job) => company === "全部公司" || job.company === company,
    );

    return [...filtered].sort((left, right) => {
      if (sort === "fit") {
        return right.score - left.score || collator.compare(left.title, right.title);
      }
      if (sort === "title") return collator.compare(left.title, right.title);
      if (sort === "location") return collator.compare(left.location, right.location);
      if (sort === "newest") return (right.firstSeenAt ?? "").localeCompare(left.firstSeenAt ?? "") || collator.compare(left.title, right.title);
      const companyOrder = companies.indexOf(left.company) - companies.indexOf(right.company);
      return companyOrder || collator.compare(left.title, right.title);
    });
  }, [company, jobsMatchingSharedFilters, sort]);

  const hasFilters = jobView !== "all" || company !== "全部公司" || (hasLocalTiers && tierFilter !== "all") || query !== "" || location !== "all" || changes !== "all" || personalFilter !== defaultPersonalFilter || availability !== "current";

  function selectJobView(view: JobView) {
    setJobView(view);
    setChanges("all");
    setPersonalFilter(defaultPersonalFilter);
    setAvailability("current");
    setSort("fit");
  }

  function showUnread(kind: "new" | "changed") {
    setTierFilter("all");
    setJobView("all");
    setCompany("全部公司");
    setQuery("");
    setLocation("all");
    setChanges(kind);
    setPersonalFilter("including-ignored");
    setAvailability("all");
  }

  function resetFilters() {
    setJobView("all");
    setCompany("全部公司");
    setQuery("");
    setLocation("all");
    setChanges("all");
    setPersonalFilter(defaultPersonalFilter);
    setAvailability("current");
    setTierFilter("all");
  }

  return (
    <main className="site-shell">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Role Radar 首页">
          <span className="brand-mark" aria-hidden="true">
            R
          </span>
          <span className="brand-copy">
            <strong>ROLE RADAR</strong>
            <small>Frontier AI careers</small>
          </span>
        </a>
        <div className="snapshot-chip">
          <span className="live-dot" aria-hidden="true" />
          数据快照 · {snapshotDate}
        </div>
      </header>

      <section className="hero" id="top">
        <div className="hero__copy">
          <p className="eyebrow">ML SYSTEMS · TRAINING INFRA</p>
          <h1>
            找到值得你
            <br />
            <em>投入的前沿。</em>
          </h1>
          <p className="hero__description">
            聚合前沿 AI 实验室、NVIDIA 与知名量化公司的美国公开岗位，优先 pretraining、SFT、
            distributed training、training performance、ML framework 与 kernel；排除 cluster
            scheduling。
          </p>
          <a className="hero-cta" href="#roles">
            浏览全部 {currentJobs.length} 个岗位 <span aria-hidden="true">↓</span>
          </a>
        </div>

        <div className="hero__signal" aria-label="公司岗位分布">
          <div className="signal-orbit" aria-hidden="true">
            <span className="orbit-dot orbit-dot--one" />
            <span className="orbit-dot orbit-dot--two" />
            <span className="orbit-dot orbit-dot--three" />
            <span className="orbit-center">{currentJobs.length}</span>
          </div>
          <div className="signal-list">
            <div className="signal-row">
              <span>已接入公司</span><strong>{companies.length}</strong>
            </div>
            <div className="signal-row">
              <span>当前岗位</span><strong>{currentJobs.length}</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="roles-section" id="roles">
        <div className="tracking-overview">
          <button className="tracking-stat" type="button" aria-pressed={changes === "new"}
            onClick={() => showUnread("new")}>
            <strong>{unreadNew}</strong><span>未读新增 · 查看</span>
          </button>
          <button className="tracking-stat" type="button" aria-pressed={changes === "changed"}
            onClick={() => showUnread("changed")}>
            <strong>{unreadChanges}</strong><span>有未读变化的岗位 · 查看</span>
          </button>
          <div><strong>{jobs.filter((job) => job.personal?.favorite).length}</strong><span>已收藏</span></div>
          <div className="tracking-overview-actions">
            <button type="button" disabled={!ready || actionBusy || radar?.refreshing} onClick={() => void runAction("refresh")}>
              {radar?.refreshing ? "正在刷新各公司…" : "刷新岗位"}
            </button>
            <button type="button" disabled={!ready || actionBusy || !(unreadNew + unreadChanges)} onClick={() => void runAction("reviewed")}>将当前全部变化标为已读</button>
          </div>
        </div>
        <p className="tracking-help">新增指首次入选本地追踪，不代表岗位刚发布。变化标为已读后不再提醒；历史记录仍保留。</p>
        {(!ready || serviceError) && <p className="service-message" role="status">{serviceError || "正在读取岗位历史与个人状态…"}<button type="button" onClick={() => void load()}>重新连接</button></p>}
        {(actionError || radar?.refreshError) && <p role="alert" className="service-message">{actionError || radar?.refreshError}</p>}
        {radar && <SourceStatus sources={radar.sources} />}
        <div className="section-heading">
          <div>
            <p className="eyebrow">OPEN ROLES</p>
            <h2>符合筛选的岗位</h2>
          </div>
          <p>
            显示 <strong>{visibleJobs.length}</strong> / {jobs.length} 条追踪记录
          </p>
        </div>

        <div className="filter-panel" role="search" aria-label="筛选岗位">
          <div className="job-view-tabs" aria-label="岗位视图">
            {Object.entries(jobViewLabels).map(([value, label]) => (
              <button key={value} type="button"
                className={`company-tab${jobView === value ? " is-active" : ""}`}
                aria-pressed={jobView === value}
                disabled={value !== "all" && !ready}
                onClick={() => selectJobView(value as JobView)}>
                {label}{value !== "all" && <span>{ready ? viewCounts[value as "latest" | "earlier"] : "—"}</span>}
              </button>
            ))}
          </div>
          {ready && radar?.latestBatch && <p className="tracking-help" role="status">
            {radar.refreshing ? "本次刷新进行中，数量持续更新" : `最近刷新：${dateLabel(radar.latestBatch.completedAt)}`}
            {" · "}当前公司、地区与搜索范围内新增 {latestAdditionCount} 个，待投 {viewCounts.latest} 个。
            <button className="addition-link" type="button" onClick={() => selectJobView("latest")}>查看本次新增 →</button>
            {["partial", "interrupted"].includes(radar.latestBatch.status) && " 部分来源未完成，请查看来源状态。"}
          </p>}
          {jobView !== "all" && <p className="tracking-help">
            仅显示当前匹配、尚未投递的新增岗位；已投递或不感兴趣后移出，标为已读不影响待投列表。
          </p>}
          <div className="company-tabs" aria-label="按公司筛选">
            <div className="company-filter-topline">
              <button
                className={company === "全部公司" ? "company-tab company-tab--all is-active" : "company-tab company-tab--all"}
                onClick={() => setCompany("全部公司")}
                type="button"
                aria-pressed={company === "全部公司"}
              >
                全部公司 <span>{jobsMatchingSharedFilters.length}</span>
              </button>
              {hasLocalTiers && <label className="local-tier-filter">
                本地分级
                <select value={tierFilter} onChange={(event) => setTierFilter(event.target.value)}>
                  <option value="all">全部公司</option>
                  <option value="1">Tier 1</option>
                  <option value="2">Tier 2</option>
                  <option value="unassigned">未分级</option>
                </select>
              </label>}
            </div>
            <div className="company-buttons">
              {companies.map((name) => (
                <button
                  className={company === name ? "company-tab is-active" : "company-tab"}
                  key={name}
                  onClick={() => setCompany(name)}
                  type="button"
                  aria-pressed={company === name}
                >
                  {name}<span>{filteredCompanyCounts[name]}</span>
                </button>
              ))}
            </div>
          </div>
          {jobView === "all" && <div className="tracking-filters">
            <label>变化<select value={changes} onChange={(event) => {
              setChanges(event.target.value);
              if (event.target.value !== "all") setAvailability("all");
            }}>
              <option value="all">全部变化状态</option><option value="new">未读新增</option><option value="changed">有未读变化</option>
            </select></label>
            <label>我的记录<select value={personalFilter} onChange={(event) => {
              setPersonalFilter(event.target.value as PersonalFilter);
              if (event.target.value === "favorites") setAvailability("all");
            }}>
              <option value="all">全部（隐藏不感兴趣）</option>
              <option value="hide-applied">全部（隐藏已投递 + 不感兴趣）</option>
              <option value="favorites">已收藏</option>
              {Object.entries(stageLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}
              <option value="including-ignored">全部（含不感兴趣）</option>
            </select></label>
            <label>岗位状态<select value={availability} onChange={(event) => setAvailability(event.target.value)}>
              <option value="current">当前匹配（含待验证）</option><option value="all">全部（含历史）</option>
              {Object.entries(availabilityLabels).filter(([value]) => value !== "active").map(([value, label]) => <option value={value} key={value}>{label}</option>)}
            </select></label>
          </div>}

          <div className="filter-controls">
            <label className="search-control">
              <span className="search-icon" aria-hidden="true" />
              <span className="sr-only">搜索职位、公司或地点</span>
              <input
                type="search"
                placeholder="搜索方向，如 training infra、SFT、kernel、runtime…"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>

            <label className="select-control">
              <span>地点</span>
              <select value={location} onChange={(event) => setLocation(event.target.value)}>
                {locationOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="select-control">
              <span>排序</span>
              <select value={sort} onChange={(event) => setSort(event.target.value as SortKey)}>
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        {visibleJobs.length > 0 ? (
          <div className="jobs-grid" aria-live="polite">
            {visibleJobs.map((job, index) => (
              <JobCard job={job} localTier={companyTiers[job.company]} index={index} key={job.id} ready={ready} onSave={savePersonal}
                sourceFailed={radar?.sources.some((source) => source.company === job.company && source.status === "failed") ?? false} />
            ))}
          </div>
        ) : (
          <div className="empty-state" role="status">
            <span aria-hidden="true">⌁</span>
            <h3>{jobView === "all" ? "没有找到符合条件的岗位" : "当前范围内没有待投的新增岗位"}</h3>
            <p>{jobView === "latest" ? "可以查看此前新增待投，或回到全部岗位继续筛选。" : "换一个关键词，或清除当前筛选条件。"}</p>
            {jobView === "latest" && <button type="button" onClick={() => selectJobView("earlier")}>查看此前新增待投</button>}
            {hasFilters && (
              <button type="button" onClick={resetFilters}>
                清除筛选
              </button>
            )}
          </div>
        )}
      </section>

      <footer className="site-footer">
        <div>
          <span className="brand-mark brand-mark--small" aria-hidden="true">
            R
          </span>
          <p>Role Radar · Local job intelligence</p>
        </div>
        <p>公开招聘页面快照 · 规则可解释 · 已排除 cluster scheduling</p>
      </footer>
    </main>
  );
}
