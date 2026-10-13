# Job Application

一个通用的本地求职管理应用，将职位发现、岗位筛选、投递跟踪和表单填写集中到同一个工作流程中，帮助你整理感兴趣的机会，跟进每一次申请。

## 可以做什么

- **发现岗位**：统一抓取已接入的 24 家公司的公开招聘来源，不预设公司等级，集中查看不同公司的机会。
- **筛选与比较**：按公司、地点和关键词浏览，查看内置规则给出的匹配理由。
- **跟踪申请**：收藏岗位，记录感兴趣、已投递或不感兴趣状态，并保存备注。
- **查看变化**：区分新发现的岗位与历史记录，了解职位描述、地点等信息的变化。
- **辅助填写**：通过 Chrome 扩展填写常见联系信息，核对后自行提交申请。

岗位历史和个人记录保存在本机。看板支持浏览与管理，命令行提供抓取和刷新入口。

## 岗位方向

不同岗位方向放在独立的 `profiles/` 子目录中，共享岗位采集、收藏、投递状态和历史记录能力。

- [ML Systems](src/job_application/profiles/ml_systems/README.md)：已有匹配规则与搜索词，当前程序仍默认使用此方向。
- [ML Research Scientist](src/job_application/profiles/ml_research_scientist/README.md)：预留目录，尚未实现。

随仓库提供的公司列表、看板和示例快照仍采用美国 ML Systems / 训练基础设施岗位配置。本次仅整理目录，尚未实现岗位方向切换或通用偏好设置。各模块边界和当前依赖见[方向目录说明](src/job_application/profiles/README.md)。

## 项目结构

项目由 Python 后端、React 看板和独立的 Chrome 扩展组成。

```text
src/job_application/  Python 包；cli.py 为命令入口
  sources/           招聘来源适配器
  profiles/          各岗位方向的搜索词与匹配规则
    ml_systems/      现有 ML Systems 方向
    ml_research_scientist/  研究科学家方向（仅目录说明）
  db/                SQLAlchemy 数据模型
  dashboard.py       默认公司来源与快照生成
  tracking.py        历史、个人状态与刷新批次
  api.py             本机 HTTP API
migrations/          Alembic 数据库迁移
tests/               Python 测试
frontend/            React + vinext/Vite 看板
chrome-autofill/     独立 Chrome 扩展及测试
docs/                环境、验证命令与公开发布说明
```

## 环境

- Python **3.11 或更高版本**（`.python-version` 固定默认 3.11）。
- [uv](https://docs.astral.sh/uv/getting-started/installation/) 用于按 `uv.lock` 安装 Python 依赖。
- Node.js **24 LTS** 推荐用于复现测试；前端要求至少 **22.13.0**，并使用 Node 原生 TypeScript 支持。
- npm，随 Node.js 安装。前端依赖固定在 `frontend/package-lock.json`。
- 本地运行以 macOS / Linux 为主；Windows 可使用 WSL。端口 3000 和 8765 需要空闲。

## 安装与启动

在本仓库根目录运行：

```bash
uv sync --frozen
cp .env.example .env
uv run alembic upgrade head
```

启动 API，并保持这个终端运行：

```bash
uv run job-application serve
```

另开一个终端，从仓库根目录启动前端：

```bash
cd frontend
npm ci
npm run dev
```

打开 <http://localhost:3000/>。前端将 `/api/radar` 请求代理到 `127.0.0.1:8765`。数据保存到仓库根目录的 `jobs.db`。前后端都保持运行即可保存收藏、投递状态和备注。

API 不可用时，看板使用 `frontend/app/jobs.ts` 的只读快照并禁用保存操作。随仓库保留的快照日期为 **2026-10-09**，只包含公开岗位摘要，不包含个人投递记录；它不代表职位目前仍然开放。

## 使用示例

查看命令：

```bash
uv run job-application --help
uv run job-application fetch --help
```

抓取单个公开招聘源（需要网络）：

```bash
uv run job-application fetch ashby "OpenAI" openai
uv run job-application fetch greenhouse "Anthropic" anthropic
```

`fetch` 获取指定招聘源的岗位，不应用看板的 ML Systems 匹配规则。公司名称和招聘源标识可按目标公司替换，使用该来源支持的真实标识。

使用当前内置的 ML Systems 规则筛选岗位：

```bash
uv run job-application match greenhouse "Anthropic" anthropic --summary
uv run job-application match workday "NVIDIA" nvidia/NVIDIAExternalCareerSite \
  --discovery-profile ml-systems --summary
```

刷新所有默认来源：

```bash
uv run job-application refresh-dashboard
```

也可以点击看板中的“刷新岗位”。刷新会更新数据库及 `frontend/app/jobs.ts`；单一来源失败不会阻止其余来源更新，失败来源保留上次成功结果。命令退出码 `2` 表示至少一个来源失败。

首次启动会将随仓库的快照导入为历史基线，不把这些旧岗位全部记作新增。后续“新增”表示本地首次入选，不等同于招聘方刚发布。搜索遗漏、规则淘汰和明确下架是不同状态；查看历史记录时选择“全部（含历史）”。

## 配置

在仓库根目录的 `.env` 中设置，或通过环境变量覆盖：

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `JOB_APPLICATION_DATABASE_URL` | `sqlite:///./jobs.db` | 本地 SQLite 数据库位置 |
| `JOB_APPLICATION_HTTP_TIMEOUT_SECONDS` | `20` | 招聘源请求超时秒数 |
| `JOB_APPLICATION_HTTP_USER_AGENT` | 见 `.env.example` | 请求的 User-Agent |

请从仓库根目录启动后端，确保相对数据库路径和快照路径一致。默认公司来源与显示信息在 `src/job_application/dashboard.py` 与 `frontend/app/ui-config.ts` 中；修改公司集合后需保持两处一致并重新生成快照。筛选规则在 `src/job_application/profiles/ml_systems/`。

### 可选的本地公司偏好

默认看板平等展示全部 24 家公司，按公司名称排序，不包含预设 Tier，也不会因公司分级跳过任何来源。

如需自己的分级，可在仓库根目录创建 `.local/company-tiers.json`，内容为 JSON 对象：公司名称作为键，`1` 或 `2` 作为值。空配置为 `{}`。未配置的公司仍正常显示。

本机 API 运行时读取此文件，看板才会显示个人分级标签和可选筛选，默认仍选择全部公司。修改后等待页面自动更新即可；删除文件可恢复无分级展示。配置错误时忽略该文件，并在后端日志提示。

`.local/` 已被 Git 忽略；分级不会写入岗位快照或前端构建。分享源码时使用 Git 导出，勿直接压缩包含个人配置的整个工作目录。

公开版本保留本地运行所需的 Cloudflare/vinext 构建适配，但已移除私有 Sites 部署配置和未使用的认证、D1 模板。本机 API 没有面向互联网的用户认证；本项目目前按单用户本地工具设计。

## Chrome 扩展

按照 [扩展安装和使用说明](chrome-autofill/README.md)，在 Chrome 扩展页面启用开发者模式并加载 `chrome-autofill/`。个人资料由扩展保存到本机 `chrome.storage.local`，不在仓库中。填写后需要自行核对并提交。

## 验证与开发

```bash
uv run pytest -q
uv run ruff check src tests
uv run mypy src/job_application
uv run python scripts/smoke.py
node --test chrome-autofill/tests/*.test.mjs
cd frontend
npm test
npm run lint
npm run typecheck
```

完整说明见 [开发与验证](docs/development.md)。API 测试需要允许监听本机临时端口；前端构建也会使用本地构建运行时。测试使用临时数据库和模拟招聘源，不执行真实投递。

## 数据与许可证

个人数据库、备份、日志、面试资料、缓存和旧 Git 历史不随此公开副本分发。后续发布时仍需复查新增文件；`.gitignore` 不能保护已经提交的敏感内容。详情见 [发布前检查](docs/publication.md)。

**尚未选择许可证。** 在公开发布前，由项目所有者确认代码及随附内容的发布权利，并选定、补充 `LICENSE`。第三方依赖和招聘信息不因本项目选择许可证而自动改变其原有权利归属。
