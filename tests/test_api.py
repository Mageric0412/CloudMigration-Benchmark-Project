"""
API Module Tests - CloudMigration-Benchmark-Project
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cloudmigration_benchmark.api import (
    BenchmarkAPI,
    HealthCheck,
    EvaluationRequest,
    EvaluationResponse,
)
from cloudmigration_benchmark.api.routes import create_api_spec


class TestHealthCheck:
    """Health check tests"""

    def test_health_check_creation(self):
        """Test HealthCheck creation"""
        health = HealthCheck(
            status="healthy",
            version="0.1.0",
            timestamp="2026-04-17T10:00:00",
        )
        assert health.status == "healthy"
        assert health.version == "0.1.0"
        assert "2026" in health.timestamp


class TestEvaluationRequest:
    """Evaluation request tests"""

    def test_request_creation(self):
        """Test EvaluationRequest creation"""
        request = EvaluationRequest(
            test_suite_path="/path/to/test.xlsx",
            dimensions=["accuracy", "safety"],
            max_samples=10,
        )
        assert request.test_suite_path == "/path/to/test.xlsx"
        assert len(request.dimensions) == 2
        assert request.max_samples == 10

    def test_request_with_config_overrides(self):
        """Test request with config overrides"""
        request = EvaluationRequest(
            test_suite_path="/path/to/test.xlsx",
            dimensions=["accuracy"],
            config_overrides={"pass_threshold": 0.9},
        )
        assert request.config_overrides["pass_threshold"] == 0.9


class TestEvaluationResponse:
    """Evaluation response tests"""

    def test_response_creation(self):
        """Test EvaluationResponse creation"""
        response = EvaluationResponse(
            status="completed",
            report_id="rpt_20260417100000",
            timestamp="2026-04-17T10:00:00",
            results={"score": 0.85},
            summary={"overall_score": 0.85},
        )
        assert response.status == "completed"
        assert "rpt_" in response.report_id
        assert response.results["score"] == 0.85


class TestBenchmarkAPI:
    """Benchmark API tests"""

    def test_api_creation(self):
        """Test BenchmarkAPI creation"""
        api = BenchmarkAPI()
        assert api.runner is None
        assert len(api.routes) > 0

    def test_api_with_runner(self):
        """Test API with custom runner"""
        from cloudmigration_benchmark import BenchmarkRunner
        runner = BenchmarkRunner()
        api = BenchmarkAPI(runner=runner)
        assert api.runner is not None

    def test_health_endpoint(self):
        """Test health endpoint"""
        api = BenchmarkAPI()
        health = api._health()
        assert health.status == "healthy"
        assert health.version == "0.1.0"

    def test_reports_endpoint(self):
        """Test reports endpoint"""
        api = BenchmarkAPI()
        reports = api._reports()
        assert "reports" in reports
        assert "count" in reports

    def test_test_suites_endpoint(self):
        """Test test suites endpoint"""
        api = BenchmarkAPI()
        suites = api._test_suites()
        assert "test_suites" in suites
        assert "count" in suites

    def test_api_to_dict(self):
        """Test API to dict conversion"""
        api = BenchmarkAPI()
        api_dict = api.to_dict()
        assert api_dict["name"] == "CloudMigration-Benchmark-API"
        assert api_dict["version"] == "0.1.0"
        assert "/health" in api_dict["endpoints"]


class TestAPISpec:
    """API specification tests"""

    def test_create_api_spec(self):
        """Test OpenAPI spec creation"""
        spec = create_api_spec()
        assert spec["openapi"] == "3.0.0"
        assert "paths" in spec
        assert "/health" in spec["paths"]
        assert "/evaluate" in spec["paths"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])