"""
Mock测试数据生成器 - CloudMigration-Benchmark-Project
"""

import json
import random
from typing import Dict, List, Any
from datetime import datetime


class MockAIResponseGenerator:
    """
    Mock AI响应生成器

    模拟不同质量级别的AI响应
    """

    # 响应模板
    RESPONSE_TEMPLATES = {
        "resource_import": [
            "我已经分析了您的IT基础设施，发现了{dict_count}个关键资源，包括：{resources}。",
            "根据您提供的信息，我识别出了{vm_count}台虚拟机和{db_count}个数据库。",
        ],
        "inventory_confirmation": [
            "已确认以下资源清单：{items}。清单完整性达到{completeness}%",
            "资源确认完成，共{count}项资源已验证。",
        ],
        "cloud_strategy": [
            "基于您的应用特点，建议采用{strategy}策略。理由：{rationale}",
            "推荐{strategy}作为首选迁移策略，次选为{alternative}",
        ],
        "spec_recommendation": [
            "根据您的工作负载，推荐以下规格：{specs}。预估月度成本：{cost}",
            "规格推荐完成，建议使用{recommended_spec}以获得最佳性价比。",
        ],
        "report_generation": [
            "迁移报告已生成，包含以下章节：{sections}。总体评估：{assessment}",
            "完整的云迁移报告已准备就绪，包括成本估算、风险评估和时间线。",
        ],
    }

    def __init__(self, quality: str = "medium"):
        """
        初始化生成器

        Args:
            quality: 响应质量级别 ("high", "medium", "low", "error")
        """
        self.quality = quality

    def generate(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """生成Mock响应"""
        dimension = test_case.get("dimension", "accuracy")
        phase = test_case.get("phase", "")

        if dimension == "latency":
            return self._generate_latency_response()
        elif dimension == "safety":
            return self._generate_safety_response()
        elif dimension == "industry_depth":
            return self._generate_industry_depth_response(phase)
        else:
            return self._generate_standard_response(test_case)

    def _generate_latency_response(self) -> Dict[str, Any]:
        """生成延迟响应"""
        if self.quality == "high":
            response_time_ms = random.uniform(100, 500)
        elif self.quality == "medium":
            response_time_ms = random.uniform(500, 1500)
        elif self.quality == "low":
            response_time_ms = random.uniform(1500, 3000)
        else:
            response_time_ms = random.uniform(3000, 5000)

        return {
            "response_time_ms": response_time_ms,
            "output": "响应内容",
        }

    def _generate_safety_response(self) -> Dict[str, Any]:
        """生成安全性响应"""
        if self.quality == "high":
            is_safe = True
        elif self.quality == "medium":
            is_safe = random.choice([True, True, True, False])
        else:
            is_safe = random.choice([True, False])

        return {
            "is_safe": is_safe,
            "output": "这是一个安全的标准响应" if is_safe else "不能处理",
        }

    def _generate_industry_depth_response(self, phase: str) -> Dict[str, Any]:
        """生成行业纵深响应"""
        responses = {
            "session_integrity": {
                "completed_phases": ["resource_import", "inventory_confirmation", "resource_summary"] if self.quality != "low" else ["resource_import"],
            },
            "interruption_recovery": {
                "post_interrupt_response": "继续上一步的操作，我们正在处理..." if self.quality != "error" else "对不起，我没有之前的上下文信息",
            },
            "context_memory": {
                "output": f"根据之前提到的{random.choice(['资源清单', '迁移策略', '成本估算'])}，我现在提供详细的分析..." if self.quality != "error" else "我没有之前的信息",
            },
            "error_handling": {
                "output": "您的输入有误，请重新提供正确的信息。具体来说，请检查以下几点：..." if self.quality != "error" else "错误",
            },
            "self_service_navigation": {
                "navigation_steps": ["导入资源", "确认清单", "选择策略"],
                "current_position": "选择策略" if self.quality != "low" else "未知",
            },
            "resource_consistency": {
                "final_resources": ["VM-001", "VM-002", "DB-001"],
            },
        }

        return responses.get(phase, {"output": "Mock响应内容"})

    def _generate_standard_response(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """生成标准响应"""
        dimension = test_case.get("dimension", "accuracy")
        expected = test_case.get("expected_output", {})

        # 根据质量级别决定匹配度
        if self.quality == "high":
            match_rate = 0.95
        elif self.quality == "medium":
            match_rate = 0.75
        elif self.quality == "low":
            match_rate = 0.5
        else:
            match_rate = 0.2

        expected_output = expected.get("output", "标准响应内容") if isinstance(expected, dict) else str(expected)

        # 生成包含或不包含预期内容的响应
        if random.random() < match_rate:
            output = expected_output
        else:
            output = f"这是{random.choice(['不同的', '部分', '错误'])}的响应内容"

        return {
            "output": output,
            "confidence": random.uniform(0.6, 0.95),
        }


def generate_test_cases(
    dimension: str = "accuracy",
    count: int = 10,
    phase: str = "general"
) -> List[Dict[str, Any]]:
    """
    生成测试用例

    Args:
        dimension: 评测维度
        count: 生成数量
        phase: 测试阶段

    Returns:
        测试用例列表
    """
    test_cases = []

    for i in range(count):
        tc = {
            "id": f"TC-{dimension.upper()}-{i+1:03d}",
            "scenario_id": f"SC-{phase}-{i+1:03d}",
            "dimension": dimension,
            "phase": phase,
            "description": f"测试用例描述 {i+1}",
            "input_data": {
                "query": f"测试查询 {i+1}",
                "context": f"测试上下文 {i+1}",
            },
            "expected_output": {
                "output": f"期望输出内容 {i+1}",
            },
            "priority": random.choice(["P0", "P1", "P2"]),
            "tags": ["test", dimension],
        }
        test_cases.append(tc)

    return test_cases


def generate_cloud_migration_test_cases(count: int = 50) -> List[Dict[str, Any]]:
    """
    生成云迁移场景的测试用例

    Args:
        count: 生成数量

    Returns:
        云迁移测试用例列表
    """
    phases = [
        "resource_import",
        "inventory_confirmation",
        "resource_summary",
        "grouping_architecture",
        "cloud_strategy",
        "preference_confirmation",
        "spec_recommendation",
        "report_generation",
    ]

    dimensions = ["accuracy", "safety", "consistency", "usability", "industry_depth"]

    test_cases = []

    for i in range(count):
        phase = random.choice(phases)
        dimension = random.choice(dimensions)

        tc = {
            "id": f"TC-CM-{i+1:04d}",
            "scenario_id": f"SC-CM-{i//10+1:02d}",
            "dimension": dimension,
            "phase": phase,
            "description": f"云迁移测试用例 - {phase}阶段",
            "input_data": {
                "query": f"用户查询关于{phase}",
                "context": {
                    "previous_phase": phases[(phases.index(phase) - 1) % len(phases)] if i > 0 else None,
                    "resource_count": random.randint(1, 100),
                },
            },
            "expected_output": {
                "output": f"期望的{phase}输出",
            },
            "priority": random.choice(["P0", "P1", "P2"]),
            "tags": ["cloud_migration", phase, dimension],
        }

        # 行业纵深特殊字段
        if dimension == "industry_depth":
            sub_dims = ["session_integrity", "interruption_recovery", "context_memory", "error_handling", "self_service_navigation", "resource_consistency"]
            tc["input_data"]["sub_dimension"] = random.choice(sub_dims)

        test_cases.append(tc)

    return test_cases


def generate_industry_depth_test_cases() -> List[Dict[str, Any]]:
    """生成行业纵深评测测试用例"""
    sub_dimensions = [
        "session_integrity",
        "interruption_recovery",
        "context_memory",
        "error_handling",
        "self_service_navigation",
        "resource_consistency",
    ]

    test_cases = []

    for sub_dim in sub_dimensions:
        for i in range(5):
            tc = {
                "id": f"TC-ID-{sub_dim}-{i+1:02d}",
                "scenario_id": f"SC-ID-{sub_dim}",
                "dimension": "industry_depth",
                "phase": sub_dim,
                "description": f"行业纵深评测 - {sub_dim}",
                "input_data": {
                    "sub_dimension": sub_dim,
                    "test_scenario": f"测试场景 {i+1}",
                },
                "expected_output": {
                    "expected_score": random.uniform(0.7, 0.95),
                },
                "priority": "P1",
                "tags": ["industry_depth", sub_dim],
            }
            test_cases.append(tc)

    return test_cases


if __name__ == "__main__":
    # 生成测试数据
    print("生成云迁移测试用例...")
    cm_cases = generate_cloud_migration_test_cases(50)
    print(f"生成 {len(cm_cases)} 个云迁移测试用例")

    print("\n生成行业纵深测试用例...")
    id_cases = generate_industry_depth_test_cases()
    print(f"生成 {len(id_cases)} 个行业纵深测试用例")

    # 保存为JSON
    output_dir = Path(__file__).parent
    with open(output_dir / "mock_test_cases.json", "w", encoding="utf-8") as f:
        json.dump({
            "cloud_migration": cm_cases,
            "industry_depth": id_cases,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n测试数据已保存到 {output_dir / 'mock_test_cases.json'}")
