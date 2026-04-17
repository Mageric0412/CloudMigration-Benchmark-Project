# CloudMigration-Benchmark-Project

AI Agent评测框架 - 专注于云迁移场景的运维能力评估。

## 功能特性

### 六大AI评测维度
| 维度 | 说明 | 评分方式 |
|------|------|----------|
| **准确性** | 答案正确性、任务完成度 | 精确匹配/公式计算 |
| **安全性** | 有害内容过滤、合规检查 | 规则引擎/AI判断 |
| **响应速度** | 响应时间、吞吐量 | 计时测量 |
| **一致性** | 多轮对话上下文保持 | 相似度计算 |
| **鲁棒性** | 抗干扰、异常输入处理 | 注入测试 |
| **可用性** | 用户体验、引导清晰度 | 任务完成率 |

### 行业纵深评测
专注于云迁移自助完成能力：
- 会话完整性评估
- 中断恢复测试
- 上下文记忆验证
- 错误处理测试
- 自助导航评估
- 资源一致性检查

### 核心能力
- **XLSX批量导入**: 支持多Sheet、多文件批量导入
- **配置驱动评分**: 每个维度独立开关，支持多种评分公式
- **响应格式支持**: 文本、链接、JSON、表格、Markdown等
- **现代化界面**: Gradio 6.x 构建，实时进度显示，交互式图表
- **报告导出**: JSON/YAML/CSV/HTML多种格式

## 快速开始

### 安装

```bash
pip install -e .
```

### 启动Web界面

```bash
python -m cloudmigration_benchmark.web.app
# 或使用命令
cmb
```

### 使用Python API

```python
from cloudmigration_benchmark.core import BenchmarkRunner

runner = BenchmarkRunner()
runner.load_test_suite("path/to/test_suite.xlsx")
results = runner.run_evaluation(dimensions=["accuracy", "safety"])
```

## XLSX评测集格式

### test_cases Sheet (必需)
| 字段 | 说明 | 必需 |
|------|------|------|
| id | 测试用例ID | ✓ |
| scenario_id | 场景ID | ✓ |
| phase | 阶段名称 | ✓ |
| dimension | 评测维度 | ✓ |
| description | 描述 | ✓ |
| input | 输入数据(JSON) | ✓ |
| expected_output | 期望输出(JSON) | |
| priority | 优先级(P0/P1/P2) | |
| tags | 标签(逗号分隔) | |

### scenarios Sheet
| 字段 | 说明 |
|------|------|
| id | 场景ID |
| name | 场景名称 |
| description | 描述 |
| test_case_ids | 关联的测试用例ID |

### config Sheet
| 字段 | 说明 |
|------|------|
| dimension | 维度名称 |
| enabled | 是否启用(true/false) |
| formula | 评分公式 |
| threshold | 通过阈值 |

## 评分公式类型

- `exact_match`: 精确匹配
- `fuzzy_match`: 模糊匹配
- `accuracy`: 准确率
- `f1_score`: F1分数
- `rouge`: ROUGE评分
- `bleu`: BLEU评分
- `ai_judge`: AI评判
- `custom`: 自定义公式

## 项目结构

```
CloudMigration-Benchmark-Project/
├── src/cloudmigration_benchmark/
│   ├── core/                      # 核心模块
│   │   ├── config.py              # 配置管理
│   │   ├── scoring_engine.py      # 评分引擎
│   │   ├── test_suite_loader.py   # XLSX加载器
│   │   └── models.py              # 数据模型
│   ├── evaluation/                 # 评测维度
│   │   ├── base.py                # 基础评估器
│   │   ├── dimensions.py          # 六大AI维度
│   │   └── industry_depth.py      # 行业纵深评测
│   └── web/                       # Web界面
│       └── app.py                 # Gradio应用
├── data/                          # 测试数据
│   ├── samples/                   # 样例xlsx
│   └── mock/                      # Mock数据
├── tests/                         # 单元测试
└── docs/                          # 文档
```

## 开发指南

### 添加新的评测维度

1. 在 `evaluation/dimensions.py` 中创建新的评估器类
2. 继承 `BaseEvaluator` 基类
3. 实现 `evaluate` 方法
4. 在 `config.py` 中注册新维度

### 自定义评分公式

在XLSX的config Sheet中配置：
```yaml
formula: "custom"
formula_params:
  weights:
    accuracy: 0.4
    completeness: 0.3
    quality: 0.3
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
