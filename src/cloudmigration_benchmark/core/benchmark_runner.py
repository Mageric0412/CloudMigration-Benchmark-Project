"""
Benchmark运行器 - CloudMigration-Benchmark-Project
核心评测执行引擎
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from cloudmigration_benchmark.core.config import BenchmarkConfig, DimensionConfig
from cloudmigration_benchmark.core.models import (
    TestCase,
    EvaluationResult,
    PhaseResult,
    BenchmarkReport,
    DimensionType,
)
from cloudmigration_benchmark.core.scoring_engine import ScoringEngine
from cloudmigration_benchmark.core.test_suite_loader import TestSuiteLoader, LoadedTestSuite


logger = logging.getLogger(__name__)


@dataclass
class EvaluationProgress:
    """评测进度"""
    total: int = 0
    completed: int = 0
    current_phase: str = ""
    current_test_case: str = ""
    current_dimension: str = ""
    results: List[EvaluationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100

    @property
    def is_complete(self) -> bool:
        """是否完成"""
        return self.completed >= self.total


class BenchmarkRunner:
    """
    Benchmark运行器

    负责:
    - 加载测试套件
    - 执行评测任务
    - 进度跟踪
    - 结果汇总
    """

    def __init__(
        self,
        config: Optional[BenchmarkConfig] = None,
        max_workers: int = 4,
        progress_callback: Optional[Callable[[EvaluationProgress], None]] = None,
    ):
        """
        初始化运行器

        Args:
            config: 基准测试配置
            max_workers: 最大并发数
            progress_callback: 进度回调函数
        """
        self.config = config or BenchmarkConfig()
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.scoring_engine = ScoringEngine()
        self.test_loader = TestSuiteLoader()
        self.logger = logging.getLogger(__name__)

        self._current_suite: Optional[LoadedTestSuite] = None
        self._progress: Optional[EvaluationProgress] = None
        self._lock = threading.Lock()

    @property
    def current_suite(self) -> Optional[LoadedTestSuite]:
        """当前测试套件"""
        return self._current_suite

    @property
    def progress(self) -> Optional[EvaluationProgress]:
        """当前进度"""
        return self._progress

    def load_test_suite(self, file_path: str) -> LoadedTestSuite:
        """
        加载测试套件

        Args:
            file_path: XLSX文件路径

        Returns:
            LoadedTestSuite对象
        """
        self._current_suite = self.test_loader.load_from_xlsx(file_path)
        self.logger.info(f"已加载测试套件: {self._current_suite.name}")
        return self._current_suite

    def load_test_suites_from_folder(self, folder_path: str) -> List[LoadedTestSuite]:
        """
        从文件夹批量加载测试套件

        Args:
            folder_path: 文件夹路径

        Returns:
            LoadedTestSuite列表
        """
        suites = self.test_loader.load_from_folder(folder_path)
        self.logger.info(f"已加载 {len(suites)} 个测试套件")
        return suites

    def run_evaluation(
        self,
        dimensions: Optional[List[str]] = None,
        phases: Optional[List[str]] = None,
        max_samples: Optional[int] = None,
    ) -> BenchmarkReport:
        """
        执行评测

        Args:
            dimensions: 要评测的维度列表，None表示全部
            phases: 要评测的阶段列表，None表示全部
            max_samples: 最大样本数，None表示全部

        Returns:
            BenchmarkReport对象
        """
        if not self._current_suite:
            raise ValueError("请先加载测试套件")

        # 获取测试用例
        test_cases = self._get_filtered_test_cases(dimensions, phases, max_samples)

        # 初始化进度
        self._progress = EvaluationProgress(
            total=len(test_cases),
            completed=0,
        )

        # 执行评测
        results = self._execute_evaluation(test_cases)

        # 生成报告
        report = self._generate_report(results)

        self.logger.info(f"评测完成: {report.passed_tests}/{report.total_tests} 通过")
        return report

    def _get_filtered_test_cases(
        self,
        dimensions: Optional[List[str]],
        phases: Optional[List[str]],
        max_samples: Optional[int],
    ) -> List[TestCase]:
        """获取过滤后的测试用例"""
        test_cases = self._current_suite.test_cases

        # 按维度过滤
        if dimensions:
            dimensions_set = set(dimensions)
            test_cases = [tc for tc in test_cases if tc.dimension in dimensions_set]

        # 按阶段过滤
        if phases:
            phases_set = set(phases)
            test_cases = [tc for tc in test_cases if tc.phase in phases_set]

        # 限制数量
        if max_samples:
            test_cases = test_cases[:max_samples]

        return test_cases

    def _execute_evaluation(self, test_cases: List[TestCase]) -> List[EvaluationResult]:
        """执行评测"""
        results = []

        for i, tc in enumerate(test_cases):
            # 更新进度
            self._update_progress(
                completed=i,
                current_test_case=tc.id,
                current_dimension=tc.dimension,
                current_phase=tc.phase,
            )

            try:
                result = self._evaluate_single(tc)
                results.append(result)
            except Exception as e:
                self.logger.error(f"评测失败 {tc.id}: {e}")
                results.append(
                    EvaluationResult(
                        test_case_id=tc.id,
                        scenario_id=tc.scenario_id,
                        dimension=tc.dimension,
                        phase=tc.phase,
                        passed=False,
                        score=0.0,
                        error_message=str(e),
                    )
                )

        # 标记完成
        self._update_progress(completed=len(test_cases))
        return results

    def _evaluate_single(self, test_case: TestCase) -> EvaluationResult:
        """评估单个测试用例"""
        start_time = time.time()

        # 获取维度配置
        dim_config = self.config.dimensions.get(
            test_case.dimension,
            DimensionConfig(name=test_case.dimension),
        )

        # 模拟AI响应 (实际应用中应调用真实的AI模型)
        actual_output = self._mock_ai_response(test_case)

        # 计算评分
        predictions = [self._extract_prediction(actual_output)]
        references = [self._extract_reference(test_case.expected_output)]

        score_result = self.scoring_engine.calculate_score(
            formula_name=dim_config.formula,
            predictions=predictions,
            references=references,
        )

        execution_time = (time.time() - start_time) * 1000

        return EvaluationResult(
            test_case_id=test_case.id,
            scenario_id=test_case.scenario_id,
            dimension=test_case.dimension,
            phase=test_case.phase,
            passed=self.scoring_engine.is_passed(score_result.score),
            score=score_result.score,
            confidence=score_result.confidence,
            response_format=test_case.response_format,
            actual_output=actual_output,
            expected_output=test_case.expected_output,
            execution_time_ms=execution_time,
            metadata=score_result.metadata,
        )

    def _mock_ai_response(self, test_case: TestCase) -> Dict[str, Any]:
        """
        模拟AI响应

        在实际应用中，这里应调用真实的AI模型API
        此处使用简化的模拟逻辑，返回与输入相关的随机响应
        """
        import random

        # 模拟不同维度的响应
        if test_case.dimension == "latency":
            return {
                "response_time_ms": random.uniform(100, 3000),
                "output": "模拟响应内容",
            }
        elif test_case.dimension == "safety":
            return {
                "is_safe": random.choice([True, True, True, False]),
                "output": "模拟安全响应",
            }
        else:
            return {
                "output": test_case.input_data.get("query", "模拟AI响应") if isinstance(test_case.input_data, dict) else str(test_case.input_data),
                "confidence": random.uniform(0.6, 0.95),
            }

    def _extract_prediction(self, output: Dict[str, Any]) -> str:
        """提取预测值"""
        if isinstance(output, dict):
            return output.get("output", str(output))
        return str(output)

    def _extract_reference(self, expected: Any) -> str:
        """提取参考值"""
        if expected is None:
            return ""
        if isinstance(expected, dict):
            return expected.get("output", str(expected))
        return str(expected)

    def _update_progress(
        self,
        completed: int,
        current_test_case: str = "",
        current_dimension: str = "",
        current_phase: str = "",
    ):
        """更新进度"""
        if self._progress:
            with self._lock:
                self._progress.completed = completed
                if current_test_case:
                    self._progress.current_test_case = current_test_case
                if current_dimension:
                    self._progress.current_dimension = current_dimension
                if current_phase:
                    self._progress.current_phase = current_phase

            # 调用回调
            if self.progress_callback:
                self.progress_callback(self._progress)

    def _generate_report(self, results: List[EvaluationResult]) -> BenchmarkReport:
        """生成评测报告"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 按维度分组
        dimension_results: Dict[str, List[EvaluationResult]] = {}
        for result in results:
            if result.dimension not in dimension_results:
                dimension_results[result.dimension] = []
            dimension_results[result.dimension].append(result)

        # 计算各维度分数
        dimension_scores = {}
        for dim, dim_results in dimension_results.items():
            scores = [r.score for r in dim_results]
            dimension_scores[dim] = sum(scores) / len(scores) if scores else 0.0

        # 按阶段分组
        phase_results: Dict[str, List[EvaluationResult]] = {}
        for result in results:
            if result.phase not in phase_results:
                phase_results[result.phase] = []
            phase_results[result.phase].append(result)

        # 计算各阶段结果
        phase_scores = {}
        for phase, phase_result_list in phase_results.items():
            phase_result = PhaseResult(phase=phase)
            for r in phase_result_list:
                phase_result.add_result(r)
            phase_scores[phase] = phase_result

        # 计算总体分数
        all_scores = [r.score for r in results]
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        return BenchmarkReport(
            timestamp=timestamp,
            total_tests=len(results),
            passed_tests=sum(1 for r in results if r.passed),
            failed_tests=sum(1 for r in results if not r.passed),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            phase_scores=phase_scores,
            dimension_results=dimension_results,
        )

    def export_report(
        self,
        report: BenchmarkReport,
        format: str = "json",
        output_path: Optional[str] = None,
    ) -> str:
        """
        导出报告

        Args:
            report: BenchmarkReport对象
            format: 导出格式 (json/yaml/csv/html)
            output_path: 输出路径，None则返回字符串

        Returns:
            报告内容或文件路径
        """
        import json
        import yaml

        if format == "json":
            content = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        elif format == "yaml":
            content = yaml.dump(report.to_dict(), allow_unicode=True, default_flow_style=False)
        elif format == "csv":
            import pandas as pd
            df = pd.DataFrame([
                {
                    "test_case_id": r.test_case_id,
                    "dimension": r.dimension,
                    "phase": r.phase,
                    "passed": r.passed,
                    "score": r.score,
                    "confidence": r.confidence,
                }
                for r in report.dimension_results.values()
            ])
            content = df.to_csv(index=False)
        else:
            raise ValueError(f"不支持的格式: {format}")

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return output_path

        return content
