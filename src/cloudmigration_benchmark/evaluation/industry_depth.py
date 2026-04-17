"""
行业纵深评测 - CloudMigration-Benchmark-Project

专注于云迁移自助完成能力的评测，包括:
1. 会话完整性 (Session Integrity)
2. 中断恢复 (Interruption Recovery)
3. 上下文记忆 (Context Memory)
4. 错误处理 (Error Handling)
5. 自助导航 (Self-Service Navigation)
6. 资源一致性 (Resource Consistency)
"""

from typing import Dict, List, Any, Optional, Set
import time
import random
import logging
from dataclasses import dataclass, field
from enum import Enum

from cloudmigration_benchmark.evaluation.base import BaseEvaluator, EvaluatorConfig
from cloudmigration_benchmark.core.models import EvaluationResult


logger = logging.getLogger(__name__)


class SessionState(Enum):
    """会话状态"""
    ACTIVE = "active"
    INTERRUPTED = "interrupted"
    RESUMED = "resumed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConversationTurn:
    """对话轮次"""
    turn_id: int
    speaker: str  # "user" or "assistant"
    content: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """会话上下文"""
    session_id: str
    user_id: str
    state: SessionState = SessionState.ACTIVE
    turns: List[ConversationTurn] = field(default_factory=list)
    collected_resources: Set[str] = field(default_factory=set)
    confirmed_items: Set[str] = field(default_factory=set)
    migration_strategy: Optional[str] = None
    interruption_point: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_turn(self, speaker: str, content: str) -> ConversationTurn:
        """添加对话轮次"""
        turn = ConversationTurn(
            turn_id=len(self.turns),
            speaker=speaker,
            content=content,
            timestamp=time.time(),
        )
        self.turns.append(turn)
        return turn


class SessionIntegrityEvaluator(BaseEvaluator):
    """
    会话完整性评估器

    评估云迁移旅程能否在不中断的情况下顺利完成全流程
    """

    # 云迁移旅程的必需阶段
    REQUIRED_PHASES = [
        "resource_import",        # 资源导入
        "inventory_confirmation", # 资源清单确认
        "resource_summary",       # 资源总结
        "grouping_architecture",  # 分组与架构确认
        "cloud_strategy",         # 云策略确认
        "preference_confirmation",# 偏好确认
        "spec_recommendation",    # 规格推荐
        "report_generation",      # 报告生成
    ]

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        super().__init__(config or EvaluatorConfig(name="session_integrity", threshold=0.75))

    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """评估会话完整性"""
        start_time = time.time()

        journey_phases = test_case.get("journey_phases", self.REQUIRED_PHASES)
        completed_phases = response.get("completed_phases", [])
        expected_output = test_case.get("expected_output", {})

        # 计算完成度
        if not journey_phases:
            completion_rate = 0.5
        else:
            completed = set(completed_phases) & set(journey_phases)
            completion_rate = len(completed) / len(journey_phases)

        # 检查关键阶段是否完成
        critical_phases = expected_output.get("critical_phases", ["resource_import", "report_generation"])
        critical_completed = sum(1 for p in critical_phases if p in completed_phases)
        critical_rate = critical_completed / len(critical_phases) if critical_phases else 1.0

        # 综合评分: 完成度70% + 关键阶段30%
        score = 0.7 * completion_rate + 0.3 * critical_rate

        passed = score >= self.config.threshold
        execution_time = self._calculate_execution_time(start_time)

        return EvaluationResult(
            test_case_id=test_case.get("id", "unknown"),
            scenario_id=test_case.get("scenario_id", ""),
            dimension="industry_depth",
            phase=test_case.get("phase", "session_integrity"),
            passed=passed,
            score=score,
            confidence=0.85,
            actual_output={
                "completed_phases": completed_phases,
                "completion_rate": completion_rate,
                "critical_rate": critical_rate,
            },
            expected_output=expected_output,
            execution_time_ms=execution_time,
            metadata={
                "sub_dimension": "session_integrity",
                "total_phases": len(journey_phases),
                "completed_count": len(completed_phases),
            },
        )


class InterruptionRecoveryEvaluator(BaseEvaluator):
    """
    中断恢复评估器

    评估会话中断后能否正确恢复并继续执行
    """

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        super().__init__(config or EvaluatorConfig(name="interruption_recovery", threshold=0.70))

    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """评估中断恢复能力"""
        start_time = time.time()

        # 模拟中断点
        interruption_point = test_case.get("interruption_point", 3)
        pre_interrupt_state = test_case.get("pre_interrupt_state", {})
        post_interrupt_response = response.get("post_interrupt_response", "")

        # 评估恢复质量
        state_preserved = self._check_state_preserved(
            pre_interrupt_state,
            post_interrupt_response,
            interruption_point,
        )
        resume_quality = self._evaluate_resume_quality(post_interrupt_response, pre_interrupt_state)
        context_continuity = self._check_context_continuity(
            test_case.get("pre_interrupt_history", []),
            post_interrupt_response,
        )

        # 综合评分
        score = (
            0.4 * state_preserved +
            0.3 * resume_quality +
            0.3 * context_continuity
        )

        passed = score >= self.config.threshold
        execution_time = self._calculate_execution_time(start_time)

        return EvaluationResult(
            test_case_id=test_case.get("id", "unknown"),
            scenario_id=test_case.get("scenario_id", ""),
            dimension="industry_depth",
            phase=test_case.get("phase", "interruption_recovery"),
            passed=passed,
            score=score,
            confidence=0.80,
            actual_output={
                "post_interrupt_response": post_interrupt_response,
                "state_preserved": state_preserved,
                "resume_quality": resume_quality,
                "context_continuity": context_continuity,
            },
            execution_time_ms=execution_time,
            metadata={
                "sub_dimension": "interruption_recovery",
                "interruption_point": interruption_point,
            },
        )

    def _check_state_preserved(
        self,
        pre_state: Dict[str, Any],
        post_response: str,
        interruption_point: int,
    ) -> float:
        """检查状态是否保留"""
        if not pre_state:
            return 0.5

        # 检查关键状态信息是否在恢复响应中体现
        preserved_count = 0
        total_count = 0

        for key, value in pre_state.items():
            total_count += 1
            if str(value).lower() in post_response.lower():
                preserved_count += 1

        return preserved_count / total_count if total_count > 0 else 0.5

    def _evaluate_resume_quality(self, post_response: str, pre_state: Dict[str, Any]) -> float:
        """评估恢复质量"""
        # 检查是否有"继续"、"接着"等衔接词
        resume_indicators = ["继续", "接着", "上一步", "之前", "resume", "continue", "previous"]
        has_indicator = any(ind.lower() in post_response.lower() for ind in resume_indicators)

        # 检查是否避免了重复之前的步骤
        repetition_penalty = 0
        for key, value in pre_state.items():
            # 简单检查: 如果完全重复之前的描述，扣分
            if str(value) in post_response:
                repetition_penalty += 0.1

        quality = 1.0 if has_indicator else 0.5
        quality = max(0.0, quality - repetition_penalty)

        return quality

    def _check_context_continuity(
        self,
        pre_history: List[Dict[str, Any]],
        post_response: str,
    ) -> float:
        """检查上下文连续性"""
        if not pre_history:
            return 0.5

        # 提取历史中的关键信息
        key_info = set()
        for msg in pre_history:
            content = str(msg.get("content", "")).lower()
            key_info.update(content.split())

        # 检查恢复响应是否延续了上下文
        if not key_info:
            return 0.5

        response_tokens = set(post_response.lower().split())
        continuity = len(key_info & response_tokens) / len(key_info)

        return continuity


class ContextMemoryEvaluator(BaseEvaluator):
    """
    上下文记忆评估器

    评估多轮对话中AI对之前信息的记忆和利用能力
    """

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        super().__init__(config or EvaluatorConfig(name="context_memory", threshold=0.75))

    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """评估上下文记忆"""
        start_time = time.time()

        conversation_history = test_case.get("conversation_history", [])
        key_entities = test_case.get("key_entities", [])
        current_response = str(response.get("output", ""))

        # 评估实体记忆
        entity_memory = self._evaluate_entity_memory(key_entities, current_response)

        # 评估历史信息引用
        history_reference = self._evaluate_history_reference(
            conversation_history,
            current_response,
        )

        # 评估矛盾检测
        contradiction_score = self._evaluate_contradiction(
            conversation_history,
            current_response,
        )

        # 综合评分
        score = (
            0.4 * entity_memory +
            0.3 * history_reference +
            0.3 * contradiction_score
        )

        passed = score >= self.config.threshold
        execution_time = self._calculate_execution_time(start_time)

        return EvaluationResult(
            test_case_id=test_case.get("id", "unknown"),
            scenario_id=test_case.get("scenario_id", ""),
            dimension="industry_depth",
            phase=test_case.get("phase", "context_memory"),
            passed=passed,
            score=score,
            confidence=0.80,
            actual_output={
                "output": current_response,
                "entity_memory": entity_memory,
                "history_reference": history_reference,
                "contradiction_score": contradiction_score,
            },
            execution_time_ms=execution_time,
            metadata={
                "sub_dimension": "context_memory",
                "key_entities_count": len(key_entities),
                "conversation_turns": len(conversation_history),
            },
        )

    def _evaluate_entity_memory(self, entities: List[str], response: str) -> float:
        """评估实体记忆"""
        if not entities:
            return 0.5

        response_lower = response.lower()
        remembered = sum(1 for e in entities if e.lower() in response_lower)

        return remembered / len(entities)

    def _evaluate_history_reference(
        self,
        history: List[Dict[str, Any]],
        response: str,
    ) -> float:
        """评估历史引用"""
        if not history:
            return 0.5

        # 检查是否引用了之前提到的内容
        reference_indicators = ["之前", "刚才", "上面", "提到", "previously", "earlier", "mentioned"]
        has_reference = any(ind.lower() in response.lower() for ind in reference_indicators)

        # 检查响应是否与历史内容相关
        history_content = " ".join(str(h.get("content", "")).lower() for h in history)
        response_tokens = set(response.lower().split())
        history_tokens = set(history_content.split())

        overlap = len(response_tokens & history_tokens)
        relevance = overlap / len(response_tokens) if response_tokens else 0

        return 0.7 * relevance + 0.3 * (1.0 if has_reference else 0.0)

    def _evaluate_contradiction(
        self,
        history: List[Dict[str, Any]],
        response: str,
    ) -> float:
        """评估矛盾检测"""
        if len(history) < 2:
            return 1.0  # 历史信息不足，无法检测矛盾

        # 简化的矛盾检测
        response_lower = response.lower()
        contradiction_indicators = ["不是", "错误", "不对", "否定", "not", "wrong", "incorrect"]
        has_contradiction = any(ind in response_lower for ind in contradiction_indicators)

        return 0.0 if has_contradiction else 1.0


class ErrorHandlingEvaluator(BaseEvaluator):
    """
    错误处理评估器

    评估AI对异常输入和错误情况的处理能力
    """

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        super().__init__(config or EvaluatorConfig(name="error_handling", threshold=0.70))

    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """评估错误处理"""
        start_time = time.time()

        error_input = test_case.get("error_input", {})
        error_type = error_input.get("type", "unknown")
        actual = str(response.get("output", ""))

        # 评估错误处理策略
        strategy_score = self._evaluate_error_strategy(actual, error_type)

        # 评估用户引导
        guidance_score = self._evaluate_error_guidance(actual, error_type)

        # 评估恢复建议
        recovery_score = self._evaluate_recovery_suggestion(actual, error_type)

        # 综合评分
        score = (
            0.4 * strategy_score +
            0.3 * guidance_score +
            0.3 * recovery_score
        )

        passed = score >= self.config.threshold
        execution_time = self._calculate_execution_time(start_time)

        return EvaluationResult(
            test_case_id=test_case.get("id", "unknown"),
            scenario_id=test_case.get("scenario_id", ""),
            dimension="industry_depth",
            phase=test_case.get("phase", "error_handling"),
            passed=passed,
            score=score,
            confidence=0.75,
            actual_output={
                "output": actual,
                "error_type": error_type,
                "strategy_score": strategy_score,
                "guidance_score": guidance_score,
                "recovery_score": recovery_score,
            },
            execution_time_ms=execution_time,
            metadata={
                "sub_dimension": "error_handling",
                "error_type": error_type,
            },
        )

    def _evaluate_error_strategy(self, response: str, error_type: str) -> float:
        """评估错误处理策略"""
        # 检查是否有适当的错误处理
        good_strategies = ["澄清", "确认", "重新", "建议", "纠正", "clarify", "confirm", "correct"]
        bad_strategies = ["忽略", "拒绝", "无法", "错误", "ignore", "refuse", "cannot"]

        good_count = sum(1 for s in good_strategies if s in response.lower())
        bad_count = sum(1 for s in bad_strategies if s in response.lower())

        score = (good_count - bad_count + 3) / 6
        return max(0.0, min(1.0, score))

    def _evaluate_error_guidance(self, response: str, error_type: str) -> float:
        """评估错误处理用户引导"""
        guidance_indicators = ["请", "需要", "应该", "尝试", "please", "need", "should", "try"]
        has_guidance = sum(1 for g in guidance_indicators if g in response.lower())

        return min(1.0, has_guidance / 2)

    def _evaluate_recovery_suggestion(self, response: str, error_type: str) -> float:
        """评估恢复建议"""
        recovery_indicators = ["可以", "建议", "尝试", "推荐", "建议您", "suggest", "recommend", "try"]
        has_recovery = any(r in response.lower() for r in recovery_indicators)

        return 1.0 if has_recovery else 0.3


class SelfServiceNavigationEvaluator(BaseEvaluator):
    """
    自助导航评估器

    评估用户能否在AI引导下自主完成迁移任务
    """

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        super().__init__(config or EvaluatorConfig(name="self_service_navigation", threshold=0.70))

    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """评估自助导航能力"""
        start_time = time.time()

        user_goal = test_case.get("user_goal", "")
        navigation_steps = test_case.get("navigation_steps", [])
        actual_steps = response.get("navigation_steps", [])
        current_position = response.get("current_position", "")

        # 评估目标理解
        goal_understanding = self._evaluate_goal_understanding(user_goal, actual_steps)

        # 评估步骤完整性
        step_completeness = self._evaluate_step_completeness(
            navigation_steps,
            actual_steps,
        )

        # 评估当前位置正确性
        position_correctness = self._evaluate_position_correctness(
            navigation_steps,
            actual_steps,
            current_position,
        )

        # 综合评分
        score = (
            0.3 * goal_understanding +
            0.4 * step_completeness +
            0.3 * position_correctness
        )

        passed = score >= self.config.threshold
        execution_time = self._calculate_execution_time(start_time)

        return EvaluationResult(
            test_case_id=test_case.get("id", "unknown"),
            scenario_id=test_case.get("scenario_id", ""),
            dimension="industry_depth",
            phase=test_case.get("phase", "self_service_navigation"),
            passed=passed,
            score=score,
            confidence=0.75,
            actual_output={
                "user_goal": user_goal,
                "navigation_steps": actual_steps,
                "current_position": current_position,
                "goal_understanding": goal_understanding,
                "step_completeness": step_completeness,
                "position_correctness": position_correctness,
            },
            execution_time_ms=execution_time,
            metadata={
                "sub_dimension": "self_service_navigation",
                "expected_steps": len(navigation_steps),
                "completed_steps": len(actual_steps),
            },
        )

    def _evaluate_goal_understanding(self, goal: str, steps: List[str]) -> float:
        """评估目标理解"""
        if not goal or not steps:
            return 0.5

        goal_tokens = set(goal.lower().split())
        steps_content = " ".join(steps).lower()
        steps_tokens = set(steps_content.split())

        overlap = len(goal_tokens & steps_tokens)
        return overlap / len(goal_tokens) if goal_tokens else 0.5

    def _evaluate_step_completeness(
        self,
        expected: List[str],
        actual: List[str],
    ) -> float:
        """评估步骤完整性"""
        if not expected:
            return 0.5

        completed = sum(1 for step in actual if any(s.lower() in step.lower() for s in expected))
        return min(1.0, completed / len(expected))

    def _evaluate_position_correctness(
        self,
        expected: List[str],
        actual: List[str],
        current: str,
    ) -> float:
        """评估当前位置正确性"""
        if not expected or not current:
            return 0.5

        # 检查当前位置是否在预期的步骤序列中
        if any(current.lower() in step.lower() for step in expected):
            return 1.0

        # 检查是否与最后一步匹配
        if expected and current.lower() == expected[-1].lower():
            return 1.0

        return 0.3


class ResourceConsistencyEvaluator(BaseEvaluator):
    """
    资源一致性评估器

    评估多轮交互中资源状态的一致性
    """

    def __init__(self, config: Optional[EvaluatorConfig] = None):
        super().__init__(config or EvaluatorConfig(name="resource_consistency", threshold=0.80))

    def evaluate(self, test_case: Dict[str, Any], response: Dict[str, Any]) -> EvaluationResult:
        """评估资源一致性"""
        start_time = time.time()

        resource_list = test_case.get("resource_list", [])
        conversation_responses = test_case.get("conversation_responses", [])
        final_resources = response.get("final_resources", [])

        # 评估资源引用一致性
        reference_consistency = self._evaluate_reference_consistency(
            resource_list,
            conversation_responses,
        )

        # 评估最终资源与初始资源的一致性
        final_consistency = self._evaluate_final_consistency(
            resource_list,
            final_resources,
        )

        # 评估资源状态一致性
        state_consistency = self._evaluate_state_consistency(
            conversation_responses,
            final_resources,
        )

        # 综合评分
        score = (
            0.3 * reference_consistency +
            0.4 * final_consistency +
            0.3 * state_consistency
        )

        passed = score >= self.config.threshold
        execution_time = self._calculate_execution_time(start_time)

        return EvaluationResult(
            test_case_id=test_case.get("id", "unknown"),
            scenario_id=test_case.get("scenario_id", ""),
            dimension="industry_depth",
            phase=test_case.get("phase", "resource_consistency"),
            passed=passed,
            score=score,
            confidence=0.85,
            actual_output={
                "final_resources": final_resources,
                "reference_consistency": reference_consistency,
                "final_consistency": final_consistency,
                "state_consistency": state_consistency,
            },
            execution_time_ms=execution_time,
            metadata={
                "sub_dimension": "resource_consistency",
                "resource_count": len(resource_list),
                "conversation_rounds": len(conversation_responses),
            },
        )

    def _evaluate_reference_consistency(
        self,
        resources: List[str],
        responses: List[str],
    ) -> float:
        """评估资源引用一致性"""
        if not resources or not responses:
            return 0.5

        # 检查所有资源是否在对话中被引用
        referenced = set()
        for resp in responses:
            resp_lower = resp.lower()
            for resource in resources:
                if resource.lower() in resp_lower:
                    referenced.add(resource)

        return len(referenced) / len(resources)

    def _evaluate_final_consistency(
        self,
        initial: List[str],
        final: List[str],
    ) -> float:
        """评估最终资源与初始资源的一致性"""
        if not initial:
            return 0.5 if not final else 1.0

        if not final:
            return 0.3

        initial_set = set(str(r).lower() for r in initial)
        final_set = set(str(r).lower() for r in final)

        overlap = len(initial_set & final_set)
        return overlap / len(initial_set)

    def _evaluate_state_consistency(
        self,
        responses: List[str],
        final: List[str],
    ) -> float:
        """评估资源状态一致性"""
        if not responses or not final:
            return 0.5

        # 简化的状态一致性检查
        # 实际应用中应该检查资源属性的变化是否合理
        final_str = " ".join(str(f).lower() for f in final)

        consistent_count = sum(1 for resp in responses if any(f.lower() in resp.lower() for f in final))
        consistency_rate = consistent_count / len(responses)

        return consistency_rate


class IndustryDepthEvaluator:
    """
    行业纵深评估器聚合器

    统一管理所有行业纵深子维度的评估器
    """

    SUB_DIMENSIONS = [
        "session_integrity",
        "interruption_recovery",
        "context_memory",
        "error_handling",
        "self_service_navigation",
        "resource_consistency",
    ]

    def __init__(self, config: Optional[Dict[str, EvaluatorConfig]] = None):
        """初始化行业纵深评估器"""
        self.evaluators: Dict[str, BaseEvaluator] = {}
        self._init_evaluators(config)

    def _init_evaluators(self, config: Optional[Dict[str, EvaluatorConfig]]):
        """初始化所有子评估器"""
        self.evaluators["session_integrity"] = SessionIntegrityEvaluator(
            config.get("session_integrity") if config else None
        )
        self.evaluators["interruption_recovery"] = InterruptionRecoveryEvaluator(
            config.get("interruption_recovery") if config else None
        )
        self.evaluators["context_memory"] = ContextMemoryEvaluator(
            config.get("context_memory") if config else None
        )
        self.evaluators["error_handling"] = ErrorHandlingEvaluator(
            config.get("error_handling") if config else None
        )
        self.evaluators["self_service_navigation"] = SelfServiceNavigationEvaluator(
            config.get("self_service_navigation") if config else None
        )
        self.evaluators["resource_consistency"] = ResourceConsistencyEvaluator(
            config.get("resource_consistency") if config else None
        )

    def get_evaluator(self, sub_dimension: str) -> Optional[BaseEvaluator]:
        """获取指定子维度的评估器"""
        return self.evaluators.get(sub_dimension)

    def get_enabled_evaluators(self) -> Dict[str, BaseEvaluator]:
        """获取所有已启用的评估器"""
        return {k: v for k, v in self.evaluators.items() if v.is_enabled}

    def evaluate(
        self,
        sub_dimension: str,
        test_case: Dict[str, Any],
        response: Dict[str, Any],
    ) -> Optional[EvaluationResult]:
        """评估指定子维度"""
        evaluator = self.get_evaluator(sub_dimension)
        if not evaluator or not evaluator.is_enabled:
            return None
        return evaluator.evaluate(test_case, response)

    def evaluate_all(
        self,
        test_case: Dict[str, Any],
        response: Dict[str, Any],
    ) -> List[EvaluationResult]:
        """评估所有启用的子维度"""
        results = []
        for sub_dim, evaluator in self.get_enabled_evaluators().items():
            try:
                result = evaluator.evaluate(test_case, response)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"评估 {sub_dim} 失败: {e}")
        return results

    def get_overall_score(self, results: List[EvaluationResult]) -> float:
        """计算综合分数"""
        if not results:
            return 0.0

        weights = {
            "session_integrity": 0.20,
            "interruption_recovery": 0.15,
            "context_memory": 0.15,
            "error_handling": 0.20,
            "self_service_navigation": 0.15,
            "resource_consistency": 0.15,
        }

        total_weight = 0.0
        weighted_sum = 0.0

        for result in results:
            sub_dim = result.metadata.get("sub_dimension", "")
            weight = weights.get(sub_dim, 1.0 / len(results))
            weighted_sum += result.score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0
