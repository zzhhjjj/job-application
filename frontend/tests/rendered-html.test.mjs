import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the job dashboard", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Role Radar — ML Systems Jobs<\/title>/i);
  assert.match(html, /ROLE RADAR/);
  assert.match(html, /ML SYSTEMS · TRAINING INFRA/);
  assert.doesNotMatch(html, /TRAINING &amp; RL INFRA/);
  assert.match(html, /符合筛选的岗位/);
  assert.match(html, /via <!-- -->Ashby/);
  assert.match(html, /via <!-- -->Greenhouse/);
  assert.match(html, /via <!-- -->Google Careers/);
  assert.match(html, /数据快照/);
  assert.match(html, /20\d\d\.\d\d\.\d\d/);
  assert.match(html, /核心匹配/);
  assert.match(html, /OpenAI/);
  assert.match(html, /Anthropic/);
  assert.match(html, /SpaceXAI/);
  assert.match(html, /Cursor/);
  assert.match(html, /Google DeepMind/);
  assert.match(html, />Google</);
  assert.match(html, /MAI Superintelligence/);
  assert.match(html, /Thinking Machines Lab/);
  assert.match(html, /Periodic Labs/);
  assert.match(html, /NVIDIA/);
  assert.match(html, /Optiver/);
  assert.match(html, /Jane Street/);
  assert.match(html, /HRT/);
  assert.match(html, /D\. E\. Shaw/);
  assert.match(html, /Citadel/);
  assert.doesNotMatch(html, /Tier [12]|核心目标|扩展目标|本地分级|class="tier-badge"/);
  assert.match(html, /已接入公司/);
  const { companies } = await import("../app/ui-config.ts");
  assert.equal(companies.length, 24);
  for (const name of companies) {
    assert.ok(html.includes(`>${name}<span>`), `Company filter missing: ${name}`);
  }
  const { jobs } = await import("../app/jobs.ts");
  for (const job of jobs) {
    assert.ok(html.includes(`data-company="${job.company}"`), `Company hidden: ${job.company}`);
  }
  assert.match(html, /via <!-- -->Official Careers/);
  assert.match(html, /via <!-- -->Workday/);
  assert.match(html, /美国公开岗位/);
  assert.match(html, /本次新增/);
  assert.match(html, /此前新增待投/);
  assert.match(html, /岗位视图/);
  assert.match(html, /未读新增/);
  assert.match(html, /未读新增 · 查看/);
  assert.match(html, /将当前全部变化标为已读/);
  assert.match(html, /刷新岗位/);
  assert.match(html, /全部（隐藏已投递 \+ 不感兴趣）/);
  assert.match(html, /已投递/);
  assert.match(html, /不感兴趣/);
  assert.match(html, /保存备注/);
  assert.match(html, /查看变化记录/);
  assert.match(html, /本次未发现/);
  assert.doesNotMatch(html, /London, UK|China, Shanghai|Germany, Remote/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});
