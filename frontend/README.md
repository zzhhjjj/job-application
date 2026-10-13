# Role Radar 看板

React 看板使用 vinext/Vite 构建，读取 Python 本机 API，并在 API 不可用时显示 `app/jobs.ts` 的只读快照。完整安装顺序见 [根目录 README](../README.md)。

```bash
# Node.js 24；从 frontend/ 运行
npm ci
npm run dev
```

打开 <http://localhost:3000/>，同时在仓库根目录运行 `uv run job-application serve`。前端固定监听本机 3000 端口，代理 `/api/radar` 到本机 8765 端口。

```bash
npm test           # 构建后运行 Node 测试，包括页面服务端渲染检查
npm run lint       # ESLint
npm run typecheck  # TypeScript 类型检查
npm run build     # 生成 dist/ 构建产物
```

`npm run start` 启动 vinext 的构建产物预览；完整本地保存和刷新流程以 `npm run dev` 的 API 代理配置为准。本仓库未配置互联网部署或云端数据库。

- `app/JobsDashboard.tsx`：看板与筛选状态。
- `app/tracking.ts`：API 数据类型和待投视图规则。
- `app/ui-config.ts`：公司与 Tier 的显示配置。
- `app/jobs.ts`：带日期的公开岗位备用快照；刷新会覆盖该文件。
- `vite.config.ts`：本地代理和构建配置，不需要私有部署项目 ID。
- `worker/index.ts`：vinext 构建运行时入口。

依赖、缓存、构建产物、运行日志和部署元数据均不应提交到 Git。
