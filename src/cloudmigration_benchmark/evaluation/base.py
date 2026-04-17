"""
基础评估器 - CloudMigration-Benchmark-Project
所有评估器的基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
import time

from cloudmigration_benchmark.core.models import EvaluationResult


logger = logging.getLogger(__name__)


@dataclass
class EvaluatorConfig:
    """评估器配置"""
    name: str
    enabled: bool = True
    threshold: float = 0.8
    timeout_ms: int = 30000
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseEvaluator(ABC):
    """
    基础评估器抽象类

    所有具体的评估器都应继承此类并实现 evaluate 方法
    """

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        """
        初始化评估器

        Args:
            config: 评估器配置
        """
        self.config = config or EvaluatorConfig(name=self.__class__.__name__)
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def name(self) -> str:
        """评估器名称"""
        return self.config.name

    @property
    def is_enabled(self) -> bool:
        """是否启用"""
        return self.config.enabled

    @abstractmethod
    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """
        评估单个测试用例

        Args:
            test_case: 测试用例数据
            response: AI响应数据

        Returns:
            EvaluationResult对象
        """
        pass

    def evaluate_batch(
        self,
        test_cases: List[Dict[str, Any]],
        responses: List[Dict[str, Any]],
    ) -> List[EvaluationResult]:
        """
        批量评估

        Args:
            test_cases: 测试用例列表
            responses: AI响应列表

        Returns:
            EvaluationResult列表
        """
        results = []
        for tc, resp in zip(test_cases, responses):
            try:
                result = self.evaluate(tc, resp)
                results.append(result)
            except Exception as e:
                self.logger.error(f"评估失败 {tc.get('id', 'unknown')}: {e}")
                results.append(
                    EvaluationResult(
                        test_case_id=tc.get("id", "unknown"),
                        scenario_id=tc.get("scenario_id", ""),
                        dimension=self.name,
                        phase=tc.get("phase", "unknown"),
                        passed=False,
                        score=0.0,
                        error_message=str(e),
                    )
                )
        return results

    def _calculate_execution_time(self, start_time: float) -> float:
        """计算执行时间(毫秒)"""
        return (time.time() - start_time) * 1000

    def _is_timeout(self, start_time: float) -> bool:
        """检查是否超时"""
        elapsed = self._calculate_execution_time(start_time)
        return elapsed > self.config.timeout_ms
