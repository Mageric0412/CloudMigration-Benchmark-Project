"""
配置管理 - CloudMigration-Benchmark-Project
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import yaml
import json
from pathlib import Path


class ScoringFormulaType(Enum):
    """评分公式类型"""
    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    ACCURACY = "accuracy"
    F1_SCORE = "f1_score"
    ROUGE = "rouge"
    BLEU = "bleu"
    AI_JUDGE = "ai_judge"
    CUSTOM = "custom"
    LATENCY = "latency"


@dataclass
class DimensionConfig:
    """维度配置"""
    name: str
    enabled: bool = True
    formula: str = "accuracy"
    threshold: float = 0.8
    weight: float = 1.0
    formula_params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DimensionConfig":
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            formula=data.get("formula", "accuracy"),
            threshold=data.get("threshold", 0.8),
            weight=data.get("weight", 1.0),
            formula_params=data.get("formula_params", {}),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "formula": self.formula,
            "threshold": self.threshold,
            "weight": self.weight,
            "formula_params": self.formula_params,
            "metadata": self.metadata,
        }


@dataclass
class BenchmarkConfig:
    """基准测试配置"""

    # 六大AI维度默认配置
    DEFAULT_DIMENSIONS: Dict[str, DimensionConfig] = field(default_factory=lambda: {
        "accuracy": DimensionConfig(
            name="accuracy",
            enabled=True,
            formula="accuracy",
            threshold=0.8,
            weight=1.0,
            formula_params={},
        ),
        "safety": DimensionConfig(
            name="safety",
            enabled=True,
            formula="ai_judge",
            threshold=0.9,
            weight=1.0,
            formula_params={},
        ),
        "latency": DimensionConfig(
            name="latency",
            enabled=True,
            formula="latency",
            threshold=0.8,
            weight=1.0,
            formula_params={"max_latency_ms": 2000},
        ),
        "consistency": DimensionConfig(
            name="consistency",
            enabled=True,
            formula="rouge",
            threshold=0.75,
            weight=1.0,
            formula_params={},
        ),
        "robustness": DimensionConfig(
            name="robustness",
            enabled=True,
            formula="accuracy",
            threshold=0.7,
            weight=1.0,
            formula_params={},
        ),
        "usability": DimensionConfig(
            name="usability",
            enabled=True,
            formula="custom",
            threshold=0.8,
            weight=1.0,
            formula_params={
                "weights": {
                    "task_completion": 0.4,
                    "guidance_clarity": 0.3,
                    "user_experience": 0.3,
                }
            },
        ),
        "industry_depth": DimensionConfig(
            name="industry_depth",
            enabled=True,
            formula="custom",
            threshold=0.75,
            weight=1.0,
            formula_params={
                "weights": {
                    "session_integrity": 0.2,
                    "interruption_recovery": 0.15,
                    "context_memory": 0.15,
                    "error_handling": 0.2,
                    "self_service_navigation": 0.15,
                    "resource_consistency": 0.15,
                }
            },
        ),
    })

    dimensions: Dict[str, DimensionConfig] = field(default_factory=dict)
    pass_threshold: float = 0.8
    critical_threshold: float = 0.6
    max_retries: int = 3
    timeout_seconds: int = 300

    def __post_init__(self):
        if not self.dimensions:
            self.dimensions = self.DEFAULT_DIMENSIONS.copy()

    @classmethod
    def from_yaml(cls, path: str) -> "BenchmarkConfig":
        """从YAML文件加载"""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, path: str) -> "BenchmarkConfig":
        """从JSON文件加载"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkConfig":
        """从字典创建"""
        dimensions = {}
        for dim_data in data.get("dimensions", []):
            dim_config = DimensionConfig.from_dict(dim_data)
            dimensions[dim_config.name] = dim_config

        return cls(
            dimensions=dimensions if dimensions else cls.DEFAULT_DIMENSIONS.copy(),
            pass_threshold=data.get("pass_threshold", 0.8),
            critical_threshold=data.get("critical_threshold", 0.6),
            max_retries=data.get("max_retries", 3),
            timeout_seconds=data.get("timeout_seconds", 300),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimensions": [dim.to_dict() for dim in self.dimensions.values()],
            "pass_threshold": self.pass_threshold,
            "critical_threshold": self.critical_threshold,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
        }

    def save_yaml(self, path: str):
        """保存为YAML文件"""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)

    def save_json(self, path: str):
        """保存为JSON文件"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def get_enabled_dimensions(self) -> List[str]:
        """获取已启用的维度列表"""
        return [name for name, dim in self.dimensions.items() if dim.enabled]

    def is_dimension_enabled(self, dimension: str) -> bool:
        """检查维度是否启用"""
        return self.dimensions.get(dimension, DimensionConfig(name=dimension)).enabled
