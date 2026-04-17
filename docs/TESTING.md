# Testing Guide — CloudMigration-Benchmark-Project

## 1. Testing Overview

### 1.1 Test Structure

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
│   ├── TestContextMemoryEvaluator
│   ├── TestErrorHandlingEvaluator
│   ├── TestSelfServiceNavigationEvaluator
│   ├── TestResourceConsistencyEvaluator
│   └── TestIndustryDepthEvaluator
└── conftest.py           # pytest配置
```

### 1.2 Test Categories

| Category | Description |
|----------|-------------|
| Unit Tests | 测试单个函数/方法的行为 |
| Integration Tests | 测试模块间交互 |
| Mock Tests | 使用Mock数据进行测试 |
| Regression Tests | 确保现有功能不被破坏 |

## 2. Running Tests

### 2.1 Basic Commands

```bash
# Run all tests
pytest tests/ -v

# Run with verbose output
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_core.py -v

# Run specific test class
pytest tests/test_core.py::TestScoringEngine -v

# Run specific test
pytest tests/test_core.py::TestScoringEngine::test_accuracy_scoring -v
```

### 2.2 Advanced Options

```bash
# Show print statements
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -v -x

# Run tests matching pattern
pytest tests/ -v -k "accuracy"

# Generate coverage report
pytest tests/ --cov=cloudmigration_benchmark --cov-report=html

# Run in parallel
pytest tests/ -v -n auto
```

## 3. Core Module Tests

### 3.1 TestConfig

```python
class TestConfig:
    def test_default_config(self):
        """测试默认配置"""
        config = BenchmarkConfig()
        assert config.pass_threshold == 0.8
        assert config.critical_threshold == 0.6

    def test_dimension_config(self):
        """测试维度配置"""
        dim_config = DimensionConfig(
            name="test",
            enabled=True,
            formula="accuracy",
            threshold=0.8,
        )
        assert dim_config.name == "test"

    def test_get_enabled_dimensions(self):
        """测试获取启用的维度"""
        config = BenchmarkConfig()
        enabled = config.get_enabled_dimensions()
        assert "accuracy" in enabled
```

### 3.2 TestScoringEngine

```python
class TestScoringEngine:
    def test_accuracy_scoring(self):
        """测试准确率评分"""
        engine = ScoringEngine()
        result = engine.calculate_score(
            formula_name="accuracy",
            predictions=["yes", "no", "yes"],
            references=["yes", "no", "yes"],
        )
        assert result.score == 1.0

    def test_exact_match(self):
        """测试精确匹配"""
        engine = ScoringEngine()
        result = engine.calculate_score(
            formula_name="exact_match",
            predictions=["apple", "banana"],
            references=["apple", "orange"],
        )
        assert result.score == 0.5

    def test_fuzzy_match(self):
        """测试模糊匹配"""
        engine = ScoringEngine()
        result = engine.calculate_score(
            formula_name="fuzzy_match",
            predictions=["apple pie", "banana split"],
            references=["apple", "banana"],
        )
        assert result.score > 0

    def test_rouge_score(self):
        """测试ROUGE评分"""
        engine = ScoringEngine()
        result = engine.calculate_score(
            formula_name="rouge",
            predictions=["the quick brown fox jumps"],
            references=["the quick fox jumps over the lazy dog"],
        )
        assert 0 <= result.score <= 1
```

### 3.3 TestModels

```python
class TestModels:
    def test_test_case_creation(self):
        """测试测试用例创建"""
        tc = TestCase(
            id="TC-001",
            scenario_id="SC-001",
            dimension="accuracy",
            phase="test",
            description="Test case",
            input_data={"query": "test"},
        )
        assert tc.id == "TC-001"

    def test_evaluation_result(self):
        """测试评估结果"""
        result = EvaluationResult(
            test_case_id="TC-001",
            scenario_id="SC-001",
            dimension="accuracy",
            phase="test",
            passed=True,
            score=0.85,
            confidence=0.9,
        )
        assert result.passed is True
        assert result.score >= 0.8
```

### 3.4 TestEvaluators

```python
class TestEvaluators:
    def test_accuracy_evaluator(self):
        """测试准确性评估器"""
        evaluator = AccuracyEvaluator()
        test_case = {
            "id": "TC-001",
            "expected_output": "correct answer",
        }
        response = {"output": "correct answer"}
        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.8

    def test_safety_evaluator(self):
        """测试安全性评估器"""
        evaluator = SafetyEvaluator()
        test_case = {"id": "TC-002"}
        response = {"output": "This is a safe response"}
        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.9

    def test_latency_evaluator(self):
        """测试延迟评估器"""
        evaluator = LatencyEvaluator()
        test_case = {"id": "TC-003"}
        response = {"response_time_ms": 500}
        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.8
```

## 4. Industry Depth Tests

### 4.1 TestSessionIntegrityEvaluator

```python
class TestSessionIntegrityEvaluator:
    def test_complete_journey(self):
        """测试完整旅程"""
        evaluator = SessionIntegrityEvaluator()
        test_case = {
            "id": "TC-SI-001",
            "journey_phases": ["resource_import", "cloud_strategy", "report_generation"],
            "expected_output": {"critical_phases": ["resource_import"]},
        }
        response = {
            "completed_phases": ["resource_import", "cloud_strategy", "report_generation"],
        }
        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.7

    def test_partial_journey(self):
        """测试部分旅程"""
        evaluator = SessionIntegrityEvaluator()
        test_case = {
            "journey_phases": ["resource_import", "cloud_strategy", "report_generation"],
            "expected_output": {},
        }
        response = {"completed_phases": ["resource_import"]}
        result = evaluator.evaluate(test_case, response)
        assert result.score < 1.0
```

### 4.2 TestInterruptionRecoveryEvaluator

```python
class TestInterruptionRecoveryEvaluator:
    def test_successful_recovery(self):
        """测试成功恢复"""
        evaluator = InterruptionRecoveryEvaluator()
        test_case = {
            "interruption_point": 3,
            "pre_interrupt_state": {"resources": ["VM-001"]},
            "pre_interrupt_history": [{"content": "我们有VM-001"}],
        }
        response = {
            "post_interrupt_response": "继续之前的操作，VM-001的资源确认已完成",
        }
        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.3

    def test_failed_recovery(self):
        """测试恢复失败"""
        evaluator = InterruptionRecoveryEvaluator()
        test_case = {
            "interruption_point": 3,
            "pre_interrupt_state": {"resources": ["VM-001"]},
        }
        response = {"post_interrupt_response": "对不起，我没有之前的上下文"}
        result = evaluator.evaluate(test_case, response)
        assert result.score < 0.7
```

## 5. Test Data Specification

### 5.1 XLSX Test Suite Format

#### test_cases Sheet

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| id | string | ✓ | 测试用例ID |
| scenario_id | string | ✓ | 场景ID |
| dimension | string | ✓ | 评测维度 |
| phase | string | ✓ | 测试阶段 |
| description | string | ✓ | 描述 |
| input_data | JSON | ✓ | 输入数据 |
| expected_output | JSON | | 期望输出 |
| priority | string | | P0/P1/P2 |
| tags | string | | 逗号分隔标签 |

#### scenarios Sheet

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| id | string | ✓ | 场景ID |
| name | string | ✓ | 场景名称 |
| description | string | | 描述 |
| test_case_ids | string | | 逗号分隔测试用例ID |

#### config Sheet

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| key | string | ✓ | 配置键 |
| value | any | ✓ | 配置值 |

### 5.2 Example Test Case

```python
test_case = {
    "id": "TC-ACC-001",
    "scenario_id": "SC-001",
    "dimension": "accuracy",
    "phase": "resource_import",
    "description": "正确识别用户描述的IT基础设施",
    "input_data": {
        "query": "我有50台Windows服务器和20台Linux服务器"
    },
    "expected_output": {
        "vm_count": 70,
        "os_types": ["Windows", "Linux"]
    },
    "priority": "P1",
    "tags": "cloud_migration,resource_discovery"
}
```

## 6. Mock Data Tests

### 6.1 MockAIResponseGenerator

```python
from cloudmigration_benchmark.data.mock.mock_test_cases import MockAIResponseGenerator

generator = MockAIResponseGenerator(quality="medium")
response = generator.generate(test_case)
```

### 6.2 Response Quality Levels

| Quality | Score Range | Description |
|---------|-------------|-------------|
| high | 0.9-1.0 | 几乎完美响应 |
| medium | 0.7-0.9 | 基本正确 |
| low | 0.5-0.7 | 部分正确 |
| error | 0.0-0.5 | 错误响应 |

## 7. Integration Tests

### 7.1 Full Evaluation Flow

```python
def test_full_evaluation_flow():
    """测试完整评测流程"""
    # 1. Load test suite
    runner = BenchmarkRunner()
    suite = runner.load_test_suite("data/samples/cloud_migration_mini_10.xlsx")
    assert len(suite.test_cases) > 0

    # 2. Run evaluation
    report = runner.run_evaluation(
        dimensions=["accuracy", "safety"],
        max_samples=10
    )
    assert report.total_tests == 10
    assert 0 <= report.overall_score <= 1

    # 3. Export report
    json_report = runner.export_report(report, format="json")
    assert "overall_score" in json_report
```

### 7.2 Parallel Evaluation

```python
def test_parallel_evaluation():
    """测试并行评测"""
    runner = BenchmarkRunner(max_workers=4)
    suite = runner.load_test_suite("test_suite.xlsx")

    # Run with parallel execution
    report = runner.run_evaluation(max_samples=100)

    # Verify results
    assert report.total_tests == 100
```

## 8. Performance Tests

### 8.1 Large Dataset Test

```python
def test_large_dataset_performance():
    """测试大数据集性能"""
    import time

    runner = BenchmarkRunner()
    suite = runner.load_test_suite("large_test_suite.xlsx")

    start_time = time.time()
    report = runner.run_evaluation(max_samples=1000)
    elapsed = time.time() - start_time

    # Should complete within reasonable time
    assert elapsed < 300  # 5 minutes max
    assert report.total_tests == 1000
```

### 8.2 Memory Usage Test

```python
def test_memory_usage():
    """测试内存使用"""
    import tracemalloc

    tracemalloc.start()
    runner = BenchmarkRunner()
    runner.load_test_suite("test_suite.xlsx")
    runner.run_evaluation(max_samples=500)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Memory should be reasonable
    assert peak < 500 * 1024 * 1024  # 500MB max
```

## 9. CI/CD Integration

### 9.1 GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e .
      - run: pip install pytest pytest-cov
      - run: pytest tests/ -v --cov=cloudmigration_benchmark
```

### 9.2 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/ruff
    rev: 0.3.0
    hooks:
      - id: ruff
```

## 10. Test Coverage

### 10.1 Coverage Targets

| Module | Target |
|--------|--------|
| core | 90% |
| evaluation | 85% |
| web | 70% |
| Overall | 85% |

### 10.2 Generate Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=cloudmigration_benchmark --cov-report=html

# Open in browser
open htmlcov/index.html

# Generate XML for CI
pytest tests/ --cov=cloudmigration_benchmark --cov-report=xml
```

## 11. Troubleshooting

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| ImportError | 包未安装 | `pip install -e .` |
| Test failures | 依赖版本不匹配 | `pip install -r requirements.txt` |
| Timeout | 测试运行太慢 | 增加timeout或优化代码 |
| Coverage low | 未覆盖的代码 | 增加测试用例 |

### 11.2 Debug Tests

```bash
# Debug specific test
pytest tests/test_core.py::TestScoringEngine::test_accuracy -v --pdb

# Show local variables on failure
pytest tests/ -v -l

# Capture warnings
pytest tests/ -v -W error
```
