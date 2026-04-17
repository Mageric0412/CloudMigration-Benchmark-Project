"""
行业纵深评测测试 - CloudMigration-Benchmark-Project
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cloudmigration_benchmark.evaluation.industry_depth import (
    SessionIntegrityEvaluator,
    InterruptionRecoveryEvaluator,
    ContextMemoryEvaluator,
    ErrorHandlingEvaluator,
    SelfServiceNavigationEvaluator,
    ResourceConsistencyEvaluator,
    IndustryDepthEvaluator,
)


class TestSessionIntegrityEvaluator:
    """会话完整性评估器测试"""

    def test_complete_journey(self):
        """测试完整旅程"""
        evaluator = SessionIntegrityEvaluator()
        test_case = {
            "id": "TC-SI-001",
            "scenario_id": "SC-ID-001",
            "dimension": "industry_depth",
            "phase": "session_integrity",
            "journey_phases": [
                "resource_import",
                "inventory_confirmation",
                "resource_summary",
                "cloud_strategy",
                "report_generation",
            ],
            "expected_output": {
                "critical_phases": ["resource_import", "report_generation"],
            },
        }
        response = {
            "completed_phases": [
                "resource_import",
                "inventory_confirmation",
                "resource_summary",
                "cloud_strategy",
                "report_generation",
            ],
        }

        result = evaluator.evaluate(test_case, response)
        assert result.dimension == "industry_depth"
        assert result.metadata["sub_dimension"] == "session_integrity"
        assert result.score >= 0.7

    def test_partial_journey(self):
        """测试部分旅程"""
        evaluator = SessionIntegrityEvaluator()
        test_case = {
            "id": "TC-SI-002",
            "scenario_id": "SC-ID-001",
            "dimension": "industry_depth",
            "phase": "session_integrity",
            "journey_phases": [
                "resource_import",
                "inventory_confirmation",
                "resource_summary",
                "cloud_strategy",
                "report_generation",
            ],
            "expected_output": {},
        }
        response = {
            "completed_phases": [
                "resource_import",
                "inventory_confirmation",
            ],
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score < 1.0


class TestInterruptionRecoveryEvaluator:
    """中断恢复评估器测试"""

    def test_successful_recovery(self):
        """测试成功恢复"""
        evaluator = InterruptionRecoveryEvaluator()
        test_case = {
            "id": "TC-IR-001",
            "scenario_id": "SC-ID-002",
            "dimension": "industry_depth",
            "phase": "interruption_recovery",
            "interruption_point": 3,
            "pre_interrupt_state": {"resources": ["VM-001", "VM-002"]},
            "pre_interrupt_history": [
                {"content": "我们有VM-001和VM-002"},
            ],
        }
        response = {
            "post_interrupt_response": "继续之前的操作，VM-001和VM-002的资源确认已完成，现在进行架构分析",
        }

        result = evaluator.evaluate(test_case, response)
        # 评估逻辑: 0.4 * state_preserved + 0.3 * resume_quality + 0.3 * context_continuity
        # 由于响应中提到了VM-001和VM-002，resume_quality会较高
        assert result.score >= 0.3

    def test_failed_recovery(self):
        """测试恢复失败"""
        evaluator = InterruptionRecoveryEvaluator()
        test_case = {
            "id": "TC-IR-002",
            "scenario_id": "SC-ID-002",
            "dimension": "industry_depth",
            "phase": "interruption_recovery",
            "interruption_point": 3,
            "pre_interrupt_state": {"resources": ["VM-001"]},
        }
        response = {
            "post_interrupt_response": "对不起，我没有之前的上下文信息",
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score < 0.7


class TestContextMemoryEvaluator:
    """上下文记忆评估器测试"""

    def test_good_memory(self):
        """测试良好记忆"""
        evaluator = ContextMemoryEvaluator()
        test_case = {
            "id": "TC-CM-001",
            "scenario_id": "SC-ID-003",
            "dimension": "industry_depth",
            "phase": "context_memory",
            "conversation_history": [
                {"content": "我们有100台虚拟机"},
                {"content": "数据库包括Oracle和MySQL"},
            ],
            "key_entities": ["100台虚拟机", "Oracle", "MySQL"],
        }
        response = {
            "output": "根据之前提到的100台虚拟机和Oracle、MySQL数据库，我现在为您推荐云迁移策略",
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.6

    def test_poor_memory(self):
        """测试记忆不佳"""
        evaluator = ContextMemoryEvaluator()
        test_case = {
            "id": "TC-CM-002",
            "scenario_id": "SC-ID-003",
            "dimension": "industry_depth",
            "phase": "context_memory",
            "conversation_history": [
                {"content": "我们有100台虚拟机"},
            ],
            "key_entities": ["100台虚拟机"],
        }
        response = {
            "output": "好的，让我为您分析",
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score < 0.5


class TestErrorHandlingEvaluator:
    """错误处理评估器测试"""

    def test_good_error_handling(self):
        """测试良好错误处理"""
        evaluator = ErrorHandlingEvaluator()
        test_case = {
            "id": "TC-EH-001",
            "scenario_id": "SC-ID-004",
            "dimension": "industry_depth",
            "phase": "error_handling",
            "error_input": {"type": "invalid_input"},
        }
        response = {
            "output": "您提供的信息不完整，请补充以下内容：1) 服务器数量 2) 数据库类型",
        }

        result = evaluator.evaluate(test_case, response)
        # 评估逻辑: 0.4 * strategy_score + 0.3 * guidance_score + 0.3 * recovery_score
        # 响应中有"请"和"补充"等指导性词汇，但缺少"建议"等恢复建议
        assert result.score >= 0.4

    def test_poor_error_handling(self):
        """测试错误处理不佳"""
        evaluator = ErrorHandlingEvaluator()
        test_case = {
            "id": "TC-EH-002",
            "scenario_id": "SC-ID-004",
            "dimension": "industry_depth",
            "phase": "error_handling",
            "error_input": {"type": "invalid_input"},
        }
        response = {
            "output": "无法处理",
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score < 0.5


class TestSelfServiceNavigationEvaluator:
    """自助导航评估器测试"""

    def test_good_navigation(self):
        """测试良好导航"""
        evaluator = SelfServiceNavigationEvaluator()
        test_case = {
            "id": "TC-SN-001",
            "scenario_id": "SC-ID-005",
            "dimension": "industry_depth",
            "phase": "self_service_navigation",
            "user_goal": "完成云迁移",
            "navigation_steps": ["导入资源", "确认清单", "选择策略", "配置规格", "生成报告"],
        }
        response = {
            "navigation_steps": ["导入资源", "确认清单", "选择策略", "配置规格", "生成报告"],
            "current_position": "配置规格",
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.6

    def test_poor_navigation(self):
        """测试导航不佳"""
        evaluator = SelfServiceNavigationEvaluator()
        test_case = {
            "id": "TC-SN-002",
            "scenario_id": "SC-ID-005",
            "dimension": "industry_depth",
            "phase": "self_service_navigation",
            "user_goal": "完成云迁移",
            "navigation_steps": ["导入资源", "确认清单"],
        }
        response = {
            "navigation_steps": ["导入资源"],
            "current_position": "未知",
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score < 0.5


class TestResourceConsistencyEvaluator:
    """资源一致性评估器测试"""

    def test_consistent_resources(self):
        """测试资源一致"""
        evaluator = ResourceConsistencyEvaluator()
        test_case = {
            "id": "TC-RC-001",
            "scenario_id": "SC-ID-006",
            "dimension": "industry_depth",
            "phase": "resource_consistency",
            "resource_list": ["VM-001", "VM-002", "DB-001"],
            "conversation_responses": [
                "识别到VM-001和VM-002",
                "另外还有DB-001",
                "最终资源包括VM-001、VM-002、DB-001",
            ],
        }
        response = {
            "final_resources": ["VM-001", "VM-002", "DB-001"],
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score >= 0.7

    def test_inconsistent_resources(self):
        """测试资源不一致"""
        evaluator = ResourceConsistencyEvaluator()
        test_case = {
            "id": "TC-RC-002",
            "scenario_id": "SC-ID-006",
            "dimension": "industry_depth",
            "phase": "resource_consistency",
            "resource_list": ["VM-001", "VM-002"],
            "conversation_responses": ["识别到VM-001"],
        }
        response = {
            "final_resources": ["VM-999"],
        }

        result = evaluator.evaluate(test_case, response)
        assert result.score < 0.5


class TestIndustryDepthEvaluator:
    """行业纵深评估器聚合测试"""

    def test_evaluator_aggregation(self):
        """测试评估器聚合"""
        evaluator = IndustryDepthEvaluator()

        # 检查所有子评估器已初始化
        assert len(evaluator.evaluators) == 6
        assert "session_integrity" in evaluator.evaluators
        assert "interruption_recovery" in evaluator.evaluators
        assert "context_memory" in evaluator.evaluators
        assert "error_handling" in evaluator.evaluators
        assert "self_service_navigation" in evaluator.evaluators
        assert "resource_consistency" in evaluator.evaluators

    def test_get_enabled_evaluators(self):
        """测试获取启用的评估器"""
        evaluator = IndustryDepthEvaluator()
        enabled = evaluator.get_enabled_evaluators()
        assert len(enabled) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
