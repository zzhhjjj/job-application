# ML Systems

当前可运行的岗位方向，覆盖训练基础设施、系统性能、GPU/加速器和机器学习框架等工程岗位。

- `discovery.py`：用于招聘来源查询的搜索词与候选标题关键词。
- `rules.py`：现有匹配、排除、评分和解释规则。
- `__init__.py`：导出 `MatchTrack`、`RuleMatch` 和 `match_ml_systems_job`。

以上文件由原 `matching/` 目录迁入，规则和搜索词不变。对应规则测试位于 `tests/profiles/ml_systems/test_rules.py`（相对于仓库根目录）。

当前公司、地区和前端默认值的位置见[方向目录说明](../README.md)。此目录尚不是可以独立加载或切换的完整配置包。
