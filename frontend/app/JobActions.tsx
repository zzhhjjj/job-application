"use client";

import { useState } from "react";
import {
  availabilityLabels, dateLabel, eventLabels, radarRequest, stageLabels,
  type JobEvent, type Personal, type TrackedJob,
} from "./tracking";

const fieldLabels: Record<string, string> = {
  title: "职位名称", locations: "地点", description_text: "JD 正文",
  job_url: "职位链接", compensation: "薪资",
};

function showValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "未提供";
  return typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

export function JobActions({ job, ready, onSave }: {
  job: TrackedJob;
  ready: boolean;
  onSave: (job: TrackedJob, patch: Partial<Personal>) => Promise<void>;
}) {
  const [draft, setDraft] = useState<string | undefined>();
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [history, setHistory] = useState<JobEvent[] | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyBusy, setHistoryBusy] = useState(false);
  const personal = job.personal;
  const enabled = ready && Boolean(personal);

  async function save(patch: Partial<Personal>) {
    setBusy(true);
    setFeedback("");
    try {
      await onSave(job, patch);
      if (patch.notes !== undefined) setDraft(undefined);
      setFeedback("已保存");
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "保存失败，请重试");
    } finally {
      setBusy(false);
    }
  }

  async function toggleHistory() {
    if (historyOpen) { setHistoryOpen(false); return; }
    setHistoryOpen(true);
    setHistoryBusy(true);
    setHistory(null);
    try {
      setHistory(await radarRequest<JobEvent[]>(`/jobs/${job.id}/history`));
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "历史读取失败，请重试");
    } finally {
      setHistoryBusy(false);
    }
  }

  return (
    <div className="job-tracking">
      <div className="tracking-meta">
        {job.availability && <span className={`availability availability--${job.availability}`}>
          {availabilityLabels[job.availability]}
        </span>}
        {job.unread?.map((kind) => <span className="unread-badge" key={kind}>{eventLabels[kind] ?? kind}</span>)}
      </div>
      {job.firstSeenAt && <p className="tracking-dates">
        {job.baseline ? "历史快照基线" : "首次入选"}：{dateLabel(job.firstSeenAt)}<br />
        {job.baseline ? "旧快照日期" : "最近发现"}：{dateLabel(job.lastSeenAt)}
      </p>}
      <div className="personal-controls">
        <button type="button" disabled={!enabled || busy} aria-pressed={personal?.favorite ?? false}
          onClick={() => void save({ favorite: !personal?.favorite })}>
          {personal?.favorite ? "★ 已收藏" : "☆ 收藏"}
        </button>
        <label>处理状态
          <select aria-label={`${job.title} 处理状态`} disabled={!enabled || busy}
            value={personal?.stage ?? "pending"}
            onChange={(event) => void save({ stage: event.target.value as Personal["stage"] })}>
            {Object.entries(stageLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
      </div>
      <details className="notes-editor">
        <summary>备注{personal?.notes ? " · 已记录" : ""}{draft !== undefined && draft !== personal?.notes ? " · 未保存" : ""}</summary>
        <textarea aria-label={`${job.title} 备注`} placeholder="记录内推联系人、投递日期或需要确认的问题…"
          disabled={!enabled || busy} maxLength={10000} value={draft ?? personal?.notes ?? ""}
          onChange={(event) => { setDraft(event.target.value); setFeedback(""); }} />
        <button type="button" disabled={!enabled || busy || draft === undefined || draft === personal?.notes}
          onClick={() => void save({ notes: draft })}>保存备注</button>
      </details>
      <button className="history-toggle" type="button" disabled={!enabled || historyBusy}
        aria-expanded={historyOpen} onClick={() => void toggleHistory()}>
        {historyBusy ? "读取历史…" : historyOpen ? "收起变化记录" : "查看变化记录"}
      </button>
      {feedback && <p role="status" className="save-feedback">{feedback}</p>}
      {historyOpen && history && <div className="job-history">
        {history.length === 0 && <p>暂无变化。旧快照作为基线导入，首次补全 JD 不计为变更。</p>}
        {history.map((event) => <section key={event.id} className="history-event">
          <strong>{eventLabels[event.kind] ?? event.kind}</strong><time>{dateLabel(event.occurredAt)}</time>
          {event.kind === "not_seen" && <p>本次搜索未返回此岗位，不代表已下架。</p>}
          {event.kind === "closed" && <p>官方职位链接返回 HTTP 404 / 410。</p>}
          {Object.entries(event.changes).map(([field, change]) => <details key={field}>
            <summary>{fieldLabels[field] ?? field}变更</summary>
            <div className="change-values"><div><b>变更前</b><pre>{showValue(change.before)}</pre></div>
              <div><b>变更后</b><pre>{showValue(change.after)}</pre></div></div>
          </details>)}
        </section>)}
      </div>}
    </div>
  );
}
