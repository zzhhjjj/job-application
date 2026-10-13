# 开发与验证

所有后端命令从仓库根目录运行。使用 `uv sync --frozen` 与 `cd frontend && npm ci` 安装锁定依赖；首次安装需要网络。Python 默认 3.11，前端建议 Node.js 24。安装会生成被忽略的环境和依赖目录。

## 快速检查

```bash
uv run ruff check src tests
uv run mypy src/job_application
uv run python scripts/smoke.py
node --test chrome-autofill/tests/*.test.mjs
```

这些检查只使用本机 CPU。smoke test 会在临时目录执行数据库迁移、CLI 帮助和快照导入，然后自动清理，不访问真实招聘源或个人数据库。成功输出 `Smoke test passed`。

## 完整验证

```bash
uv run pytest -q
cd frontend
npm test
npm run lint
npm run typecheck
```

Python 测试覆盖招聘源解析、匹配、迁移、追踪与 API 冲突处理。API 测试使用本机随机端口和临时数据库。前端测试先生成 `frontend/dist/`，然后验证待投视图规则与服务端渲染。检查退出码应全部为 0；缓存和构建文件不应发布。

受限沙箱若报 `Operation not permitted` / `EPERM` 且发生在 socket bind 阶段，应在允许本机端口的环境补跑；不要把这类环境错误改成跳过测试。

## 网络集成检查

```bash
uv run job-application match ashby "OpenAI" openai --summary
uv run job-application refresh-dashboard
```

这两项访问真实招聘源；刷新还会更新数据库、历史记录及前端快照。它们不是离线 smoke test，不包含在 CI 中。招聘网站可能限流、拒绝请求或改变格式，现有模拟测试不能证明所有实时来源当前可用。

## CI

`.github/workflows/checks.yml` 在 push 和 pull request 时验证 Python 3.11 / Node.js 24 的上述检查。工作流未配置 GitHub 发布、部署或远端数据刷新。本地成功不等于远端 CI 已运行。
