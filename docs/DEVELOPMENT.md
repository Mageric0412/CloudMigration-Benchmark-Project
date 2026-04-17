# Development Guide — CloudMigration-Benchmark-Project

## 1. Project Overview

### 1.1 Project Structure

```
CloudMigration-Benchmark-Project/
├── src/cloudmigration_benchmark/
│   ├── __init__.py                 # 包入口
│   ├── core/                      # 核心模块
│   │   ├── __init__.py
│   │   ├── benchmark_runner.py    # 评测运行器
│   │   ├── config.py             # 配置管理
│   │   ├── models.py             # 数据模型
│   │   ├── scoring_engine.py     # 评分引擎
│   │   └── test_suite_loader.py  # XLSX加载器
│   ├── evaluation/               # 评测模块
│   │   ├── __init__.py
│   │   ├── base.py              # 基础评估器
│   │   ├── dimensions.py        # 六大AI维度
│   │   └── industry_depth.py    # 行业纵深评测
│   ├── web/                     # Web界面
│   │   ├── __init__.py
│   │   └── app.py              # Gradio应用
│   └── api/                     # API接口
│       └── __init__.py
├── data/                         # 测试数据
│   ├── samples/                 # 样例文件
│   ├── mock/                   # Mock数据
│   └── test_suites/            # 评测集
├── tests/                       # 单元测试
├── docs/                        # 文档
├── README.md
├── CLAUDE.md
└── pyproject.toml
```

### 1.2 Module Dependencies

```
┌─────────────────────────────────────────────────────────┐
│                      Web Layer (app.py)                  │
│         Gradio UI, Charts, User Interactions            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Core Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │   Config    │  │   Models    │  │    Loader    │  │
│  └─────────────┘  └─────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │              BenchmarkRunner                       │  │
│  │         (评测执行引擎)                            │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │              ScoringEngine                         │  │
│  │           (配置驱动评分系统)                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Evaluation Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ Dimensions  │  │Industry    │  │   Base       │  │
│  │ Evaluator  │  │  Depth     │  │  Evaluator   │  │
│  └─────────────┘  └─────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 2. Core Module API Reference

### 2.1 BenchmarkRunner

```python
from cloudmigration_benchmark.core import BenchmarkRunner

runner = BenchmarkRunner(
    config=None,           # BenchmarkConfig, None则使用默认
    max_workers=4,        # 最大并发数
    progress_callback=None # 进度回调函数
)
```

#### Methods

**`load_test_suite(file_path: str) -> LoadedTestSuite`**
```python
# 加载测试套件
suite = runner.load_test_suite("path/to/test_suite.xlsx")
print(f"测试用例数: {len(suite.test_cases)}")
```

**`load_test_suites_from_folder(folder_path: str) -> List[LoadedTestSuite]`**
```python
# 批量加载测试套件
suites = runner.load_test_suites_from_folder("data/test_suites/")
```

**`run_evaluation(...) -> BenchmarkReport`**
```python
# 执行评测
report = runner.run_evaluation(
    dimensions=["accuracy", "safety"],  # 要评测的维度
    phases=None,                       # 要评测的阶段，None表示全部
    max_samples=100                    # 最大样本数
)
print(f"总分: {report.overall_score}")
```

**`export_report(...) -> str`**
```python
# 导出报告
json_report = runner.export_report(report, format="json")
```

### 2.2 ScoringEngine

```python
from cloudmigration_benchmark.core import ScoringEngine

engine = ScoringEngine(config=None)
```

#### Supported Scoring Formulas

| Formula | Description |
|---------|-------------|
| `accuracy` | 精确匹配/模糊匹配准确率 |
| `exact_match` | 精确匹配 |
| `fuzzy_match` | 模糊匹配 |
| `f1_score` | F1分数 |
| `rouge` | ROUGE评分 |
| `bleu` | BLEU评分 |
| `ai_judge` | AI评判 |
| `latency` | 延迟评分 |
| `custom` | 自定义权重公式 |

#### Methods

**`calculate_score(...) -> ScoreResult`**
```python
result = engine.calculate_score(
    formula_name="accuracy",
    predictions=["yes", "no", "yes"],
    references=["yes", "no", "yes"],
    additional_metrics=None
)
print(f"分数: {result.score}")
print(f"等级: {result.level.value}")
```

**`is_passed(score: float) -> bool`**
```python
passed = engine.is_passed(0.85)
```

### 2.3 TestSuiteLoader

```python
from cloudmigration_benchmark.core import TestSuiteLoader

loader = TestSuiteLoader()
```

#### Methods

**`load_from_xlsx(file_path: str) -> LoadedTestSuite`**
```python
suite = loader.load_from_xlsx("test_suite.xlsx")
```

**`load_from_folder(folder_path: str, pattern: str = "*.xlsx") -> List[LoadedTestSuite]`**
```python
suites = loader.load_from_folder("data/samples/")
```

**`get_sheet_info(file_path: str) -> List[Dict]`**
```python
# 获取Sheet预览信息
info = loader.get_sheet_info("test_suite.xlsx")
for sheet in info:
    print(f"Sheet: {sheet['name']}, Type: {sheet['type']}, Rows: {sheet['rows']}")
```

## 3. Evaluation Module API Reference

### 3.1 BaseEvaluator

```python
from cloudmigration_benchmark.evaluation import BaseEvaluator, EvaluationResult

class MyEvaluator(BaseEvaluator):
    def evaluate(self, test_case: Dict, response: Dict) -> EvaluationResult:
        # 实现评估逻辑
        pass
```

### 3.2 DimensionEvaluators

```python
from cloudmigration_benchmark.evaluation.dimensions import (
    AccuracyEvaluator,
    SafetyEvaluator,
    LatencyEvaluator,
    ConsistencyEvaluator,
    RobustnessEvaluator,
    UsabilityEvaluator,
    DimensionEvaluator,
)

# 单独使用
evaluator = AccuracyEvaluator()
result = evaluator.evaluate(test_case, response)

# 聚合使用
aggregator = DimensionEvaluator()
results = aggregator.evaluate_all(test_case, response)
```

### 3.3 IndustryDepthEvaluators

```python
from cloudmigration_benchmark.evaluation.industry_depth import (
    IndustryDepthEvaluator,
    SessionIntegrityEvaluator,
    InterruptionRecoveryEvaluator,
    ContextMemoryEvaluator,
    ErrorHandlingEvaluator,
    SelfServiceNavigationEvaluator,
    ResourceConsistencyEvaluator,
)

# 行业纵深评估聚合器
evaluator = IndustryDepthEvaluator()
results = evaluator.evaluate_all(test_case, response)

# 计算综合分数
overall = evaluator.get_overall_score(results)
```

## 4. Data Models

### 4.1 TestCase

```python
from cloudmigration_benchmark.core import TestCase

tc = TestCase(
    id="TC-001",
    scenario_id="SC-001",
    dimension="accuracy",
    phase="resource_import",
    description="测试用例描述",
    input_data={"query": "用户查询"},
    expected_output={"output": "期望输出"},
    priority="P1",
    tags=["tag1", "tag2"],
    timeout_ms=30000,
    response_format="text"
)
```

### 4.2 EvaluationResult

```python
from cloudmigration_benchmark.core import EvaluationResult

result = EvaluationResult(
    test_case_id="TC-001",
    scenario_id="SC-001",
    dimension="accuracy",
    phase="test",
    passed=True,
    score=0.85,
    confidence=0.90,
    actual_output={"output": "实际输出"},
    expected_output={"output": "期望输出"},
    execution_time_ms=150.5
)
```

### 4.3 BenchmarkReport

```python
from cloudmigration_benchmark.core import BenchmarkReport

report = BenchmarkReport(
    timestamp="2026-04-17 10:00:00",
    total_tests=100,
    passed_tests=85,
    failed_tests=15,
    overall_score=0.85,
    dimension_scores={"accuracy": 0.88, "safety": 0.92},
    phase_scores={...},
    dimension_results={...}
)

# 转换为字典
report_dict = report.to_dict()
```

## 5. Configuration

### 5.1 BenchmarkConfig

```python
from cloudmigration_benchmark.core import BenchmarkConfig

config = BenchmarkConfig(
    dimensions={
        "accuracy": DimensionConfig(
            name="accuracy",
            enabled=True,
            formula="accuracy",
            threshold=0.8,
            weight=1.0
        )
    },
    pass_threshold=0.8,
    critical_threshold=0.6,
    max_retries=3,
    timeout_seconds=300
)
```

### 5.2 DimensionConfig

```python
from cloudmigration_benchmark.core import DimensionConfig

dim_config = DimensionConfig(
    name="accuracy",
    enabled=True,
    formula="accuracy",
    threshold=0.8,
    weight=1.0,
    formula_params={"custom_param": "value"},
    metadata={"description": "准确性评测"}
)
```

### 5.3 YAML Configuration

```yaml
# config.yaml
dimensions:
  - name: accuracy
    enabled: true
    formula: accuracy
    threshold: 0.8
    weight: 1.0
  - name: safety
    enabled: true
    formula: ai_judge
    threshold: 0.9
    weight: 1.0

pass_threshold: 0.8
critical_threshold: 0.6
max_retries: 3
timeout_seconds: 300
```

**Load from YAML:**
```python
config = BenchmarkConfig.from_yaml("config.yaml")
```

## 6. Web Interface API

### 6.1 Launch Application

```python
from cloudmigration_benchmark.web.app import create_app

app = create_app()
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    show_error=True
)
```

### 6.2 Gradio Components

| Component | Description |
|-----------|-------------|
| `gr.File` | XLSX文件上传 |
| `gr.CheckboxGroup` | 多选评测维度 |
| `gr.Slider` | 样本数量控制 |
| `gr.Plot` | 图表展示 |
| `gr.DataFrame` | 数据表格 |
| `gr.Markdown` | Markdown渲染 |

## 7. Development Guidelines

### 7.1 Adding New Dimension

1. 在 `evaluation/dimensions.py` 中创建新的评估器类
2. 继承 `BaseEvaluator` 基类
3. 实现 `evaluate` 方法
4. 在 `DimensionEvaluator._init_evaluators` 中注册

```python
class MyDimensionEvaluator(BaseEvaluator):
    def evaluate(self, test_case: Dict, response: Dict) -> EvaluationResult:
        # 评估逻辑
        pass
```

### 7.2 Adding New Industry Depth Sub-dimension

1. 在 `evaluation/industry_depth.py` 中创建新的评估器类
2. 继承 `BaseEvaluator` 基类
3. 实现 `evaluate` 方法
4. 在 `IndustryDepthEvaluator._init_evaluators` 中注册

### 7.3 Custom Scoring Formula

```python
# 在 config 中定义
config = {
    "formulas": {
        "my_custom_formula": {
            "type": "custom",
            "weights": {
                "accuracy": 0.4,
                "completeness": 0.3,
                "quality": 0.3
            },
            "thresholds": {
                "pass": 0.8,
                "warning": 0.7
            }
        }
    }
}
```

## 8. Testing

### 8.1 Run Tests

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_core.py -v

# 运行特定测试类
pytest tests/test_core.py::TestScoringEngine -v

# 生成覆盖率报告
pytest tests/ --cov=cloudmigration_benchmark --cov-report=html
```

### 8.2 Test Structure

```
tests/
├── test_core.py           # 核心模块测试
│   ├── TestConfig
│   ├── TestScoringEngine
│   ├── TestModels
│   └── TestEvaluators
├── test_industry_depth.py # 行业纵深测试
│   ├── TestSessionIntegrityEvaluator
│   ├── TestInterruptionRecoveryEvaluator
│   └── ...
└── conftest.py           # pytest配置
```

## 9. Package Management

### 9.1 Install in Development Mode

```bash
pip install -e .
```

### 9.2 Install Dependencies

```bash
# Core dependencies
pip install gradio pandas openpyxl plotly pyyaml numpy

# Dev dependencies
pip install pytest pytest-asyncio black ruff mypy
```

### 9.3 Build Package

```bash
python -m build
```

## 10. Best Practices

### 10.1 Code Style

- Follow PEP 8
- Use type hints
- Docstrings for public APIs
- Max line length: 100

### 10.2 Error Handling

```python
try:
    result = runner.run_evaluation(...)
except ValueError as e:
    logger.error(f"Invalid configuration: {e}")
    raise
except Exception as e:
    logger.error(f"Evaluation failed: {e}")
    raise
```

### 10.3 Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Loading test suite from {file_path}")
logger.debug(f"Loaded {len(test_cases)} test cases")
logger.warning(f"Score {score} below threshold {threshold}")
logger.error(f"Evaluation failed: {e}")
```

### 10.4 Performance

- Use `ThreadPoolExecutor` for parallel evaluation
- Cache scoring configurations
- Lazy load XLSX files
- Use generators for large result sets
