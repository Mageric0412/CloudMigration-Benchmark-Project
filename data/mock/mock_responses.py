"""
Mock响应数据 - CloudMigration-Benchmark-Project
"""

from typing import Dict, List, Any
import random


class MockAIResponse:
    """Mock AI响应类"""

    # 高质量响应
    HIGH_QUALITY = {
        "accuracy": {"output": "正确的响应内容", "confidence": 0.95},
        "safety": {"is_safe": True, "output": "安全的响应"},
        "latency": {"response_time_ms": 350, "output": "快速响应"},
        "consistency": {"output": "上下文保持一致的响应"},
        "robustness": {"output": "正确处理异常输入"},
        "usability": {"output": "用户友好的清晰指导"},
    }

    # 中等质量响应
    MEDIUM_QUALITY = {
        "accuracy": {"output": "基本正确的响应内容", "confidence": 0.75},
        "safety": {"is_safe": True, "output": "基本安全的响应"},
        "latency": {"response_time_ms": 1200, "output": "正常速度响应"},
        "consistency": {"output": "基本保持上下文一致"},
        "robustness": {"output": "部分处理异常输入"},
        "usability": {"output": "基本可用的指导"},
    }

    # 低质量响应
    LOW_QUALITY = {
        "accuracy": {"output": "部分错误的响应", "confidence": 0.55},
        "safety": {"is_safe": False, "output": "包含问题的响应"},
        "latency": {"response_time_ms": 2800, "output": "较慢的响应"},
        "consistency": {"output": "上下文有偏差"},
        "robustness": {"output": "未能处理异常"},
        "usability": {"output": "指导不清晰"},
    }

    # 错误响应
    ERROR_CASE = {
        "accuracy": {"output": "", "confidence": 0.0},
        "safety": {"is_safe": False, "output": "ERROR"},
        "latency": {"response_time_ms": 5000, "output": ""},
        "consistency": {"output": "N/A"},
        "robustness": {"output": "FAIL"},
        "usability": {"output": "无法提供帮助"},
    }

    @classmethod
    def get_response(cls, dimension: str, quality: str = "medium") -> Dict[str, Any]:
        """获取指定维度和质量的Mock响应"""
        quality_map = {
            "high": cls.HIGH_QUALITY,
            "medium": cls.MEDIUM_QUALITY,
            "low": cls.LOW_QUALITY,
            "error": cls.ERROR_CASE,
        }

        responses = quality_map.get(quality, cls.MEDIUM_QUALITY)
        return responses.get(dimension, responses["accuracy"])


# 行业纵深Mock响应
INDUSTRY_DEPTH_RESPONSES = {
    "session_integrity": [
        {
            "completed_phases": ["resource_import", "inventory_confirmation", "resource_summary",
                                "grouping_architecture", "cloud_strategy", "preference_confirmation",
                                "spec_recommendation", "report_generation"],
            "completion_rate": 1.0,
        },
        {
            "completed_phases": ["resource_import", "inventory_confirmation"],
            "completion_rate": 0.25,
        },
    ],
    "interruption_recovery": [
        {
            "post_interrupt_response": "继续我们之前的讨论。根据您之前提到的资源清单，我现在继续进行架构确认...",
            "state_preserved": True,
            "resume_quality": 0.9,
        },
        {
            "post_interrupt_response": "对不起，我没有找到之前的对话记录。",
            "state_preserved": False,
            "resume_quality": 0.2,
        },
    ],
    "context_memory": [
        {
            "output": "根据之前提到的100台虚拟机和5个数据库，我现在为您推荐云迁移策略...",
            "entity_memory_score": 0.95,
            "history_reference_score": 0.9,
        },
        {
            "output": "好的，让我为您分析...",
            "entity_memory_score": 0.3,
            "history_reference_score": 0.2,
        },
    ],
    "error_handling": [
        {
            "output": "您提供的信息不完整，请补充以下内容：1) 服务器数量 2) 数据库类型 3) 存储需求",
            "error_handling_score": 0.9,
            "user_guidance_score": 0.85,
        },
        {
            "output": "无法处理",
            "error_handling_score": 0.1,
            "user_guidance_score": 0.0,
        },
    ],
    "self_service_navigation": [
        {
            "navigation_steps": ["导入资源", "确认清单", "选择策略", "配置规格", "生成报告"],
            "current_position": "配置规格",
            "navigation_score": 0.8,
        },
        {
            "navigation_steps": ["导入资源"],
            "current_position": "未知",
            "navigation_score": 0.2,
        },
    ],
    "resource_consistency": [
        {
            "final_resources": ["VM-001", "VM-002", "VM-003", "DB-001", "DB-002"],
            "consistency_score": 0.95,
        },
        {
            "final_resources": ["VM-001", "VM-999"],
            "consistency_score": 0.4,
        },
    ],
}


def get_mock_response(dimension: str, sub_dimension: str = None, quality: str = "medium") -> Dict[str, Any]:
    """
    获取Mock响应

    Args:
        dimension: 维度名称
        sub_dimension: 子维度名称（行业纵深）
        quality: 质量级别

    Returns:
        Mock响应数据
    """
    if dimension == "industry_depth" and sub_dimension:
        responses = INDUSTRY_DEPTH_RESPONSES.get(sub_dimension, [])
        if responses:
            if quality == "high":
                return responses[0]
            elif quality == "low":
                return responses[-1]
            else:
                return random.choice(responses)

    return MockAIResponse.get_response(dimension, quality)
