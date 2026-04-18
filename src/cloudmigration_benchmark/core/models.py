"""
数据模型定义 - CloudMigration-Benchmark-Project
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime


class DimensionType(Enum):
    """评测维度类型"""
    ACCURACY = "accuracy"
    SAFETY = "safety"
    LATENCY = "latency"
    CONSISTENCY = "consistency"
    ROBUSTNESS = "robustness"
    USABILITY = "usability"
    INDUSTRY_DEPTH = "industry_depth"


class ScoreLevel(Enum):
    """评分等级"""
    EXCELLENT = "excellent"      # >= 0.9
    GOOD = "good"                # >= 0.8
    PASS = "pass"                # >= 0.6
    FAIL = "fail"                # < 0.6


class ResponseFormat(Enum):
    """响应格式类型"""
    TEXT = "text"
    LINK = "link"
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"
    CODE = "code"
    MARKDOWN = "markdown"


@dataclass
class TestCase:
    """测试用例"""
    __test__ = False  # Tell pytest not to collect this as a test class
    id: str
    scenario_id: str
    dimension: str
    phase: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None
    priority: str = "P1"
    tags: List[str] = field(default_factory=list)
    timeout_ms: int = 30000
    retry_count: int = 0
    response_format: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.input_data, str):
            import json
            try:
                self.input_data = json.loads(self.input_data)
            except json.JSONDecodeError:
                self.input_data = {"raw": self.input_data}
        if isinstance(self.expected_output, str):
            import json
            try:
                self.expected_output = json.loads(self.expected_output)
            except json.JSONDecodeError:
                self.expected_output = {"raw": self.expected_output}
        if isinstance(self.tags, str):
            self.tags = [t.strip() for t in self.tags.split(",")]


@dataclass
class Scenario:
    """测试场景"""
    id: str
    name: str
    description: str
    test_case_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """单次评测结果"""
    test_case_id: str
    scenario_id: str
    dimension: str
    phase: str
    passed: bool
    score: float
    confidence: float = 0.0
    response_format: str = "text"
    actual_output: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def score_level(self) -> ScoreLevel:
        """获取评分等级"""
        if self.score >= 0.9:
            return ScoreLevel.EXCELLENT
        elif self.score >= 0.8:
            return ScoreLevel.GOOD
        elif self.score >= 0.6:
            return ScoreLevel.PASS
        else:
            return ScoreLevel.FAIL


@dataclass
class PhaseResult:
    """阶段评测结果"""
    phase: str
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    average_score: float = 0.0
    average_confidence: float = 0.0
    results: List[EvaluationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_result(self, result: EvaluationResult):
        """添加评测结果"""
        self.results.append(result)
        self.total_tests += 1
        if result.passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        # 更新平均分
        total = len(self.results)
        self.average_score = sum(r.score for r in self.results) / total
        self.average_confidence = sum(r.confidence for r in self.results) / total

    @property
    def pass_rate(self) -> float:
        """通过率"""
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests


@dataclass
class ScoreResult:
    """评分结果"""
    score: float
    confidence: float
    level: ScoreLevel
    components: Dict[str, float]
    formula_used: str
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkReport:
    """完整评测报告"""
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_score: float
    dimension_scores: Dict[str, float]
    phase_scores: Dict[str, PhaseResult]
    dimension_results: Dict[str, List[EvaluationResult]]
    export_formats: List[str] = field(default_factory=lambda: ["json", "yaml", "csv"])

    @property
    def pass_rate(self) -> float:
        """总体通过率"""
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "pass_rate": self.pass_rate,
            "overall_score": self.overall_score,
            "dimension_scores": self.dimension_scores,
            "phase_scores": {
                phase: {
                    "total": pr.total_tests,
                    "passed": pr.passed_tests,
                    "failed": pr.failed_tests,
                    "pass_rate": pr.pass_rate,
                    "average_score": pr.average_score,
                }
                for phase, pr in self.phase_scores.items()
            }
        }
