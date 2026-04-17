"""
评分引擎 - CloudMigration-Benchmark-Project
配置驱动的评分系统，支持多种评分公式
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import Counter

from cloudmigration_benchmark.core.config import ScoringFormulaType, DimensionConfig
from cloudmigration_benchmark.core.models import ScoreResult, ScoreLevel


logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"       # >= 0.9
    MEDIUM = "medium"  # >= 0.7
    LOW = "low"        # >= 0.5
    VERY_LOW = "very_low"  # < 0.5


@dataclass
class ScoringFormula:
    """评分公式配置"""
    name: str
    type: str
    weights: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)


# 默认配置常量 (放在类外部避免dataclass可变默认值问题)
DEFAULT_SCORING_CONFIG: Dict[str, Any] = {
    "formulas": {
        "accuracy": {
            "type": "accuracy",
            "weights": {"correct": 1.0, "total": 1.0},
            "thresholds": {"pass": 0.80, "warning": 0.70},
        },
        "f1_score": {
            "type": "f1",
            "weights": {"precision": 0.5, "recall": 0.5},
            "thresholds": {"pass": 0.75, "warning": 0.65},
        },
        "response_quality": {
            "type": "custom",
            "weights": {"relevance": 0.4, "coherence": 0.3, "fluency": 0.3},
            "thresholds": {"pass": 0.75, "warning": 0.65},
        },
        "migration_success": {
            "type": "custom",
            "weights": {
                "resource_discovery": 0.20,
                "strategy_recommendation": 0.30,
                "cost_estimation": 0.25,
                "risk_identification": 0.25,
            },
            "thresholds": {"pass": 0.80, "warning": 0.70},
        },
    },
    "confidence": {
        "levels": {"high": 0.90, "medium": 0.70, "low": 0.50},
        "calculation_method": "sample_size_based",
        "min_samples_for_high_confidence": 30,
        "variance_threshold": 0.05,
    },
    "pass_threshold": 0.80,
    "critical_threshold": 0.60,
}


class ScoringEngine:
    """
    配置驱动的评分引擎

    支持的评分公式类型:
    - exact_match: 精确匹配
    - fuzzy_match: 模糊匹配
    - accuracy: 准确率
    - f1_score: F1分数
    - rouge: ROUGE评分
    - bleu: BLEU评分
    - ai_judge: AI评判
    - latency: 延迟评分
    - custom: 自定义公式
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化评分引擎

        Args:
            config: 配置字典，None则使用默认配置
        """
        self.config = config or DEFAULT_SCORING_CONFIG.copy()
        self.logger = logging.getLogger(__name__)

    def calculate_score(
        self,
        formula_name: str,
        predictions: List[Any],
        references: List[Any],
        additional_metrics: Optional[Dict[str, float]] = None,
    ) -> ScoreResult:
        """
        计算评分

        Args:
            formula_name: 公式名称
            predictions: 预测结果列表
            references: 参考结果列表
            additional_metrics: 额外的指标

        Returns:
            ScoreResult对象
        """
        formula_type = self._get_formula_type(formula_name)

        # 根据公式类型计算分数
        if formula_type == ScoringFormulaType.EXACT_MATCH:
            score = self._calc_exact_match(predictions, references)
        elif formula_type == ScoringFormulaType.FUZZY_MATCH:
            score = self._calc_fuzzy_match(predictions, references)
        elif formula_type == ScoringFormulaType.ACCURACY:
            score = self._calc_accuracy(predictions, references)
        elif formula_type == ScoringFormulaType.F1_SCORE:
            score = self._calc_f1(predictions, references)
        elif formula_type == ScoringFormulaType.ROUGE:
            score = self._calc_rouge(predictions, references)
        elif formula_type == ScoringFormulaType.BLEU:
            score = self._calc_bleu(predictions, references)
        elif formula_type == ScoringFormulaType.LATENCY:
            score = self._calc_latency(predictions, references)
        elif formula_type == ScoringFormulaType.AI_JUDGE:
            score = self._calc_ai_judge(predictions, references)
        else:
            score = self._calc_custom(predictions, references, formula_name, additional_metrics)

        # 计算置信度
        confidence = self._calculate_confidence(len(predictions))
        level = self._get_score_level(score)
        warnings = self._check_warnings(formula_name, score)

        return ScoreResult(
            score=score,
            confidence=confidence,
            level=level,
            components=additional_metrics or {},
            formula_used=formula_name,
            warnings=warnings,
        )

    def _get_formula_type(self, formula_name: str) -> ScoringFormulaType:
        """获取公式类型"""
        formula_map = {
            "exact_match": ScoringFormulaType.EXACT_MATCH,
            "fuzzy_match": ScoringFormulaType.FUZZY_MATCH,
            "accuracy": ScoringFormulaType.ACCURACY,
            "f1_score": ScoringFormulaType.F1_SCORE,
            "f1": ScoringFormulaType.F1_SCORE,
            "rouge": ScoringFormulaType.ROUGE,
            "bleu": ScoringFormulaType.BLEU,
            "ai_judge": ScoringFormulaType.AI_JUDGE,
            "latency": ScoringFormulaType.LATENCY,
            "custom": ScoringFormulaType.CUSTOM,
        }
        return formula_map.get(formula_name, ScoringFormulaType.ACCURACY)

    def _calc_exact_match(self, predictions: List[Any], references: List[Any]) -> float:
        """精确匹配评分"""
        if not predictions or not references:
            return 0.0
        correct = sum(1 for p, r in zip(predictions, references) if p == r)
        return correct / len(predictions)

    def _calc_fuzzy_match(self, predictions: List[Any], references: List[Any]) -> float:
        """模糊匹配评分 (考虑类型转换和部分匹配)"""
        if not predictions or not references:
            return 0.0

        correct = 0
        for p, r in zip(predictions, references):
            p_str = str(p).strip().lower()
            r_str = str(r).strip().lower()

            # 尝试类型转换后比较
            try:
                if float(p) == float(r):
                    correct += 1
                    continue
            except (ValueError, TypeError):
                pass

            # 精确匹配
            if p_str == r_str:
                correct += 1
                continue

            # 部分匹配 (reference 是 prediction 的子串)
            if r_str in p_str or p_str in r_str:
                correct += 1

        return correct / len(predictions)

    def _calc_accuracy(self, predictions: List[Any], references: List[Any]) -> float:
        """计算准确率"""
        if not predictions:
            return 0.0
        correct = sum(1 for p, r in zip(predictions, references) if self._is_correct(p, r))
        return correct / len(predictions)

    def _is_correct(self, prediction: Any, reference: Any) -> bool:
        """判断预测是否正确"""
        # 精确匹配
        if prediction == reference:
            return True
        # 尝试数值比较
        try:
            if float(prediction) == float(reference):
                return True
        except (ValueError, TypeError):
            pass
        # 字符串忽略大小写比较
        if isinstance(prediction, str) and isinstance(reference, str):
            if prediction.strip().lower() == reference.strip().lower():
                return True
        return False

    def _calc_f1(self, predictions: List[Any], references: List[Any]) -> float:
        """计算F1分数"""
        try:
            from sklearn.metrics import f1_score
            # 转换为字符串进行计算
            pred_str = [str(p) for p in predictions]
            ref_str = [str(r) for r in references]
            f1 = f1_score(ref_str, pred_str, average="weighted", zero_division=0)
            return float(f1)
        except ImportError:
            self.logger.warning("sklearn未安装，使用简化版F1计算")
            return self._calc_accuracy(predictions, references)

    def _calc_rouge(self, predictions: List[str], references: List[str]) -> float:
        """计算ROUGE评分 (简化版)"""
        rouge_scores = []
        for pred, ref in zip(predictions, references):
            pred_tokens = str(pred).lower().split()
            ref_tokens = str(ref).lower().split()

            if not pred_tokens or not ref_tokens:
                rouge_scores.append(0.0)
                continue

            # 计算LCS
            lcs_length = self._lcs_length(pred_tokens, ref_tokens)
            precision = lcs_length / len(pred_tokens) if pred_tokens else 0
            recall = lcs_length / len(ref_tokens) if ref_tokens else 0

            if precision + recall == 0:
                rouge_scores.append(0.0)
            else:
                f_score = 2 * precision * recall / (precision + recall)
                rouge_scores.append(f_score)

        return np.mean(rouge_scores) if rouge_scores else 0.0

    def _lcs_length(self, seq1: List, seq2: List) -> int:
        """计算最长公共子序列长度"""
        m, n = len(seq1), len(seq2)
        prev = [0] * (n + 1)

        for i in range(1, m + 1):
            curr = [0] * (n + 1)
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    curr[j] = prev[j - 1] + 1
                else:
                    curr[j] = max(prev[j], curr[j - 1])
            prev = curr

        return prev[n]

    def _calc_bleu(self, predictions: List[str], references: List[str]) -> float:
        """计算BLEU分数 (简化版)"""
        bleu_scores = []

        for pred, ref in zip(predictions, references):
            pred_tokens = str(pred).lower().split()
            ref_tokens = str(ref).lower().split()

            if not pred_tokens:
                bleu_scores.append(0.0)
                continue

            # 简化的unigram精确率
            pred_unigrams = Counter(pred_tokens)
            ref_unigrams = Counter(ref_tokens)

            overlap = sum((pred_unigrams & ref_unigrams).values())
            precision = overlap / len(pred_tokens)

            # 简短惩罚
            ref_len = len(ref_tokens)
            pred_len = len(pred_tokens)

            if pred_len >= ref_len:
                bp = 1.0
            else:
                bp = np.exp(1 - ref_len / pred_len) if pred_len > 0 else 0.0

            bleu_scores.append(bp * precision)

        return np.mean(bleu_scores) if bleu_scores else 0.0

    def _calc_latency(self, predictions: List[Any], references: List[Any]) -> float:
        """
        计算延迟评分

        predictions: 实际延迟时间(毫秒)列表
        references: 最大允许延迟时间(毫秒)列表
        """
        if not predictions:
            return 0.0

        scores = []
        for actual, max_allowed in zip(predictions, references):
            try:
                actual_ms = float(actual)
                max_ms = float(max_allowed)
                if actual_ms <= max_ms:
                    scores.append(1.0)
                else:
                    # 超过延迟时间，逐渐扣分
                    ratio = max(0, 1 - (actual_ms - max_ms) / max_ms)
                    scores.append(ratio)
            except (ValueError, TypeError):
                scores.append(0.5)

        return np.mean(scores) if scores else 0.0

    def _calc_ai_judge(self, predictions: List[Any], references: List[Any]) -> float:
        """
        AI评判评分 - 模拟AI对预测结果的质量判断

        在实际实现中，这里可以调用AI模型来判断预测质量
        此处使用简化的模拟逻辑
        """
        if not predictions or not references:
            return 0.5

        scores = []
        for pred, ref in zip(predictions, references):
            # 简化的模拟评分逻辑
            pred_str = str(pred).lower()
            ref_str = str(ref).lower()

            # 计算关键词重叠度
            pred_words = set(pred_str.split())
            ref_words = set(ref_str.split())

            if not ref_words:
                scores.append(0.5)
                continue

            overlap = len(pred_words & ref_words) / len(ref_words)
            scores.append(overlap)

        return np.mean(scores) if scores else 0.0

    def _calc_custom(
        self,
        predictions: List[Any],
        references: List[Any],
        formula_name: str,
        additional_metrics: Optional[Dict[str, float]],
    ) -> float:
        """使用自定义权重计算分数"""
        if not additional_metrics:
            return self._calc_accuracy(predictions, references)

        # 获取配置的权重
        formula_config = self.config.get("formulas", {}).get(formula_name, {})
        weights = formula_config.get("weights", {})

        if not weights:
            return np.mean(list(additional_metrics.values())) if additional_metrics else 0.0

        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0

        score = 0.0
        for metric_name, weight in weights.items():
            if metric_name in additional_metrics:
                score += additional_metrics[metric_name] * (weight / total_weight)

        return score

    def _calculate_confidence(self, sample_count: int) -> float:
        """基于样本数量计算置信度"""
        method = self.config.get("confidence", {}).get("calculation_method", "sample_size_based")
        min_samples = self.config.get("confidence", {}).get("min_samples_for_high_confidence", 30)

        if method == "fixed":
            return 0.85

        if sample_count >= min_samples:
            return 0.95
        elif sample_count >= min_samples // 2:
            return 0.85
        elif sample_count >= min_samples // 4:
            return 0.70
        else:
            return 0.50

    def _get_score_level(self, score: float) -> ScoreLevel:
        """根据分数获取等级"""
        if score >= 0.9:
            return ScoreLevel.EXCELLENT
        elif score >= 0.8:
            return ScoreLevel.GOOD
        elif score >= 0.6:
            return ScoreLevel.PASS
        else:
            return ScoreLevel.FAIL

    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """根据置信度值获取等级"""
        levels = self.config.get("confidence", {}).get("levels", {})
        if confidence >= levels.get("high", 0.90):
            return ConfidenceLevel.HIGH
        elif confidence >= levels.get("medium", 0.70):
            return ConfidenceLevel.MEDIUM
        elif confidence >= levels.get("low", 0.50):
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _check_warnings(self, formula_name: str, score: float) -> List[str]:
        """检查并生成警告信息"""
        warnings = []
        formula_config = self.config.get("formulas", {}).get(formula_name, {})
        thresholds = formula_config.get("thresholds", {})

        if "pass" in thresholds and score < thresholds["pass"]:
            warnings.append(f"分数({score:.3f})低于通过阈值({thresholds['pass']})")
        if "warning" in thresholds and score < thresholds["warning"]:
            warnings.append(f"分数({score:.3f})低于警告阈值({thresholds['warning']})")

        return warnings

    def is_passed(self, score: float) -> bool:
        """判断是否通过"""
        return score >= self.config.get("pass_threshold", 0.8)

    def is_critical(self, score: float) -> bool:
        """判断是否处于危险水平"""
        return score < self.config.get("critical_threshold", 0.6)

    def aggregate_scores(self, scores: List[float], weights: Optional[Dict[str, float]] = None) -> float:
        """
        聚合多个分数

        Args:
            scores: 分数列表
            weights: 权重字典 (可选)

        Returns:
            聚合后的分数
        """
        if not scores:
            return 0.0

        if weights:
            total_weight = sum(weights.values())
            if total_weight > 0:
                return sum(s * w for s, w in zip(scores, weights.values())) / total_weight

        return np.mean(scores)
