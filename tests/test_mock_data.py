"""
Mock Data Tests - CloudMigration-Benchmark-Project
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "data"))

# Import mock data directly
from mock.mock_responses import (
    MockAIResponse,
    INDUSTRY_DEPTH_RESPONSES,
    get_mock_response,
)
from mock.mock_test_cases import (
    MockAIResponseGenerator,
    generate_test_cases,
    generate_cloud_migration_test_cases,
    generate_industry_depth_test_cases,
)


class TestMockAIResponse:
    """Mock AI response tests"""

    def test_high_quality_response(self):
        """Test high quality mock response"""
        response = MockAIResponse.get_response("accuracy", "high")
        assert response["confidence"] == 0.95
        assert response["output"] == "正确的响应内容"

    def test_medium_quality_response(self):
        """Test medium quality mock response"""
        response = MockAIResponse.get_response("accuracy", "medium")
        assert response["confidence"] == 0.75
        assert "基本正确" in response["output"]

    def test_low_quality_response(self):
        """Test low quality mock response"""
        response = MockAIResponse.get_response("accuracy", "low")
        assert response["confidence"] == 0.55

    def test_error_case_response(self):
        """Test error case mock response"""
        response = MockAIResponse.get_response("accuracy", "error")
        assert response["confidence"] == 0.0
        assert response["output"] == ""

    def test_all_dimensions(self):
        """Test all dimension responses"""
        dimensions = ["accuracy", "safety", "latency", "consistency", "robustness", "usability"]
        for dim in dimensions:
            response = MockAIResponse.get_response(dim, "high")
            assert dim in response or "output" in response

    def test_safety_response_structure(self):
        """Test safety response structure"""
        response = MockAIResponse.get_response("safety", "high")
        assert "is_safe" in response
        assert response["is_safe"] is True
        assert "output" in response


class TestIndustryDepthResponses:
    """Industry depth responses tests"""

    def test_session_integrity_responses(self):
        """Test session integrity responses"""
        responses = INDUSTRY_DEPTH_RESPONSES["session_integrity"]
        assert len(responses) >= 2
        assert "completed_phases" in responses[0]
        assert "completion_rate" in responses[0]

    def test_interruption_recovery_responses(self):
        """Test interruption recovery responses"""
        responses = INDUSTRY_DEPTH_RESPONSES["interruption_recovery"]
        assert len(responses) >= 2
        assert "state_preserved" in responses[0]
        assert "resume_quality" in responses[0]

    def test_context_memory_responses(self):
        """Test context memory responses"""
        responses = INDUSTRY_DEPTH_RESPONSES["context_memory"]
        assert len(responses) >= 2
        assert "entity_memory_score" in responses[0]

    def test_error_handling_responses(self):
        """Test error handling responses"""
        responses = INDUSTRY_DEPTH_RESPONSES["error_handling"]
        assert len(responses) >= 2
        assert "error_handling_score" in responses[0]

    def test_self_service_navigation_responses(self):
        """Test self service navigation responses"""
        responses = INDUSTRY_DEPTH_RESPONSES["self_service_navigation"]
        assert len(responses) >= 2
        assert "navigation_score" in responses[0]

    def test_resource_consistency_responses(self):
        """Test resource consistency responses"""
        responses = INDUSTRY_DEPTH_RESPONSES["resource_consistency"]
        assert len(responses) >= 2
        assert "consistency_score" in responses[0]


class TestGetMockResponse:
    """get_mock_response function tests"""

    def test_get_mock_response_dimension(self):
        """Test get_mock_response with dimension only"""
        response = get_mock_response("accuracy", quality="high")
        assert "output" in response
        assert "confidence" in response

    def test_get_mock_response_industry_depth(self):
        """Test get_mock_response with industry depth"""
        response = get_mock_response("industry_depth", "session_integrity", "high")
        assert "completed_phases" in response
        assert "completion_rate" in response

    def test_get_mock_response_quality(self):
        """Test get_mock_response with different qualities"""
        high_resp = get_mock_response("accuracy", quality="high")
        low_resp = get_mock_response("accuracy", quality="low")
        assert high_resp["confidence"] > low_resp["confidence"]


class TestMockTestCases:
    """Mock test cases tests"""

    def test_mock_ai_response_generator(self):
        """Test MockAIResponseGenerator"""
        generator = MockAIResponseGenerator(quality="high")
        test_case = {"dimension": "accuracy", "phase": "test", "expected_output": {"output": "test"}}
        response = generator.generate(test_case)
        assert response is not None
        assert "output" in response

    def test_generate_test_cases(self):
        """Test generate_test_cases function"""
        cases = generate_test_cases("accuracy", count=5)
        assert len(cases) == 5
        assert cases[0]["dimension"] == "accuracy"

    def test_generate_cloud_migration_test_cases(self):
        """Test generate_cloud_migration_test_cases function"""
        cases = generate_cloud_migration_test_cases(10)
        assert len(cases) == 10
        assert all("dimension" in tc for tc in cases)

    def test_generate_industry_depth_test_cases(self):
        """Test generate_industry_depth_test_cases function"""
        cases = generate_industry_depth_test_cases()
        assert len(cases) == 30  # 6 sub-dimensions * 5 cases each
        sub_dims = set(tc["phase"] for tc in cases)
        assert len(sub_dims) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])