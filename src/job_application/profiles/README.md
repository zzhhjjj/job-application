# 岗位方向（profiles）

通用的职位采集、数据模型和投递跟踪由项目共享；特定岗位方向的搜索词与匹配规则放在各自目录中。

| 目录 | 方向 | 当前状态 |
| --- | --- | --- |
| [ml_systems](ml_systems/README.md) | ML Systems | 已有规则和搜索词；仍为程序默认方向 |
| [ml_research_scientist](ml_research_scientist/README.md) | ML Research Scientist | 仅预留目录，尚无实现 |

```text
profiles/
  __init__.py
  ml_systems/
    __init__.py
    discovery.py    # 现有搜索词
    rules.py        # 现有匹配规则、评分和理由
    README.md
  ml_research_scientist/
    README.md       # 方向说明；不提供可运行配置
```

## 与通用模块的边界

- `sources/`：不同招聘网站的采集与解析，各方向共享。
- `domain/`、`db/`、`tracking.py`：岗位、数据库、收藏及投递历史，各方向共享。
- `profiles/<方向>/`：该方向的搜索词、匹配依据及评分。
- `frontend/`、`chrome-autofill/`：岗位展示与表单填写。

本次仅整理已有代码的位置。命令行和看板仍显式使用 ML Systems，没有方向注册器、自动加载或切换入口；创建一个目录不会让它成为可运行方向。

当前公司来源、美国地点过滤和部分 ML Systems 特殊处理仍在 `dashboard.py`；命令行默认值在 `cli.py`，前端公司、标签和快照在 `frontend/app/`。这些是后续支持方向切换时需要处理的现有依赖，本次保留原行为。

未来切换方向应选择搜索词与匹配规则，复用同一份岗位和个人投递记录。地区和目标公司是独立偏好，不应被固定为某个职业方向的定义。本次不实现这些能力，也不新增配置格式或抽象接口。
