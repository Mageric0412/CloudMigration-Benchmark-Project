"""
单元测试 - CloudMigration-Benchmark-Project
"""

import pytest
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cloudmigration_benchmark.core.config import BenchmarkConfig, DimensionConfig
from cloudmigration_benchmark.core.scoring_engine import ScoringEngine
from cloudmigration_benchmark.core.models import TestCase, EvaluationResult
from cloudmigration_benchmark.evaluation.dimensions import (
    AccuracyEvaluator,
    SafetyEvaluator,
    LatencyEvaluator,
    ConsistencyEvaluator,
    RobustnessEvaluator,
    UsabilityEvaluator,
)


class TestConfig:
    """配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = BenchmarkConfig()
        assert config.pass_threshold == 0.8
        assert config.critical_threshold == 0.6
        assert len(config.dimensions) >= 6

    def test_dimension_config(self):
        """测试维度配置"""
        dim_config = DimensionConfig(
            name="test",
            enabled=True,
            formula="accuracy",
            threshold=0.8,
        )
        assert dim_config.name == "test"
        assert dim_config.enabled is True
        assert dim_config.formula == "accuracy"

    def test_get_enabled_dimensions(self):
        """测试获取启用的维度"""
        config = BenchmarkConfig()
        enabled = config.get_enabled_dimensions()
        assert "accuracy" in enabled
        assert "safety" in enabled


class TestScoringEngine:
    """评分引擎测试"""

    def test_accuracy_scoring(self):
        """测试准确率评分"""
        engine = ScoringEngine()
        result = engine.calculate_score(
            formula_name="accuracy",
            predictions=["yes", "no", "yes"],
            references=["yes", "no", "yes"],
        )
        assert result.score == 1.0
        assert result.level.value in ["excellent", "good", "pass"]

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

    def test_bleu_score(self):
        """测试BLEU评分"""
        engine = ScoringEngine()
        result = engine.calculate_score(
            formula_name="bleu",
            predictions=["the quick brown fox jumps"],
            references=["the quick brown fox jumps over"],
        )
        assert 0 <= result.score <= 1

    def test_is_passed(self):
        """测试通过判断"""
        engine = ScoringEngine()
        assert engine.is_passed(0.85) is True
        assert engine.is_passed(0.5) is False

    def test_is_critical(self):
        """测试危险判断"""
        engine = ScoringEngine()
        assert engine.is_critical(0.5) is True
        assert engine.is_critical(0.7) is False


class TestModels:
    """数据模型测试"""

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
        assert tc.dimension == "accuracy"

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
        assert result.score == 0.85
        assert result.score_level.value in ["excellent", "good"]


class TestEvaluators:
    """评估器测试"""

    def test_accuracy_evaluator(self):
        """测试准确性评估器"""
        evaluator = AccuracyEvaluator()
        test_case = {
            "id": "TC-001",
            "scenario_id": "SC-001",
            "dimension": "accuracy",
            "phase": "test",
            "expected_output": "correct answer",
        }
        response = {"output": "correct answer"}

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "accuracy"
        assert result.score >= 0.8

    def test_safety_evaluator(self):
        """测试安全性评估器"""
        evaluator = SafetyEvaluator()
        test_case = {
            "id": "TC-002",
            "scenario_id": "SC-001",
            "dimension": "safety",
            "phase": "test",
        }
        response = {"output": "This is a safe response"}

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "safety"
        assert result.score >= 0.9

    def test_latency_evaluator(self):
        """测试延迟评估器"""
        evaluator = LatencyEvaluator()
        test_case = {
            "id": "TC-003",
            "scenario_id": "SC-001",
            "dimension": "latency",
            "phase": "test",
        }
        response = {"response_time_ms": 500}

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "latency"
        assert result.score >= 0.8

    def test_consistency_evaluator(self):
        """测试一致性评估器"""
        evaluator = ConsistencyEvaluator()
        test_case = {
            "id": "TC-004",
            "scenario_id": "SC-001",
            "dimension": "consistency",
            "phase": "test",
            "expected_context": {"key": "value"},
        }
        response = {"output": "The key value is preserved in context"}

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "consistency"

    def test_robustness_evaluator(self):
        """测试鲁棒性评估器"""
        evaluator = RobustnessEvaluator()
        test_case = {
            "id": "TC-005",
            "scenario_id": "SC-001",
            "dimension": "robustness",
            "phase": "test",
            "input_data": {"noise": "[noise] actual content"},
        }
        response = {"output": "actual content"}

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "robustness"

    def test_usability_evaluator(self):
        """测试可用性评估器"""
        evaluator = UsabilityEvaluator()
        test_case = {
            "id": "TC-006",
            "scenario_id": "SC-001",
            "dimension": "usability",
            "phase": "test",
            "expected_task": {"required_steps": ["step1", "step2", "step3"]},
        }
        response = {"output": "First step1, then step2, finally step3"}

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "usability"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
