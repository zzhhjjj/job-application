import { dateLabel, type SourceHealth } from "./tracking";

const statusLabels = { never: "尚未验证", running: "刷新中", ok: "抓取成功", partial: "部分未验证", failed: "刷新失败 · 保留旧数据" };

export function SourceStatus({ sources }: { sources: SourceHealth[] }) {
  const issues = sources.filter((source) => source.status === "failed" || source.status === "partial" || source.status === "never");
  return <details className="source-status">
    <summary>来源状态与覆盖范围 · {sources.length} 家公司{issues.length ? ` · ${issues.length} 家需留意` : ""}</summary>
    <p>成功时间仅代表配置范围内的抓取完成。“本次未发现”不等于下架；失败来源保留上次数据。</p>
    <div className="source-status-grid">
      {sources.map((source) => <article key={source.company}>
        <div><strong>{source.company}</strong><span className={`source-state source-state--${source.status}`}>{statusLabels[source.status]}</span></div>
        <p>{source.coverage}</p>
        <dl><dt>最近尝试</dt><dd>{dateLabel(source.lastAttempt)}</dd>
          <dt>最近成功</dt><dd>{dateLabel(source.lastSuccess)}</dd>
          <dt>上次结果</dt><dd>{source.discoveredCount} 个候选 / {source.matchedCount} 个匹配</dd></dl>
        {source.error && <p className="source-error">{source.error}</p>}
      </article>)}
    </div>
  </details>;
}
