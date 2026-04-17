"""
CloudMigration-Benchmark-Project
AI Agent评测框架 - 专注于云迁移场景的运维能力评估
"""

__version__ = "0.1.0"
__author__ = "Mageric"

from cloudmigration_benchmark.core import (
    BenchmarkRunner,
    ScoringEngine,
    TestSuiteLoader,
    BenchmarkConfig,
)
from cloudmigration_benchmark.evaluation import (
    BaseEvaluator,
    DimensionEvaluator,
    IndustryDepthEvaluator,
)

__all__ = [
    "BenchmarkRunner",
    "ScoringEngine",
    "TestSuiteLoader",
    "BenchmarkConfig",
    "BaseEvaluator",
    "DimensionEvaluator",
    "IndustryDepthEvaluator",
]
