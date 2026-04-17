"""
API Routes for CloudMigration-Benchmark-Project.

Provides REST API endpoints for:
- Benchmark execution
- Test suite management
- Report generation
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass
class EvaluationRequest:
    """Request model for evaluation API."""
    test_suite_path: str
    dimensions: List[str]
    max_samples: Optional[int] = None
    config_overrides: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationResponse:
    """Response model for evaluation API."""
    status: str
    report_id: str
    timestamp: str
    results: Dict[str, Any]
    summary: Dict[str, float]


@dataclass
class HealthCheck:
    """Health check response model."""
    status: str
    version: str
    timestamp: str


class BenchmarkAPI:
    """
    REST API for CloudMigration Benchmark.

    Example usage:
    ```python
    from cloudmigration_benchmark.api import BenchmarkAPI

    api = BenchmarkAPI()
    api.start(port=8080)
    ```
    """

    def __init__(self, runner=None):
        """
        Initialize API with optional BenchmarkRunner.

        Args:
            runner: BenchmarkRunner instance. If None, creates new instance.
        """
        self.runner = runner
        self.routes = {
            "/health": self._health,
            "/evaluate": self._evaluate,
            "/reports": self._reports,
            "/test-suites": self._test_suites,
        }

    def _health(self) -> HealthCheck:
        """Health check endpoint."""
        return HealthCheck(
            status="healthy",
            version="0.1.0",
            timestamp=datetime.now().isoformat(),
        )

    def _evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Execute benchmark evaluation.

        Args:
            request: EvaluationRequest with test suite and configuration

        Returns:
            EvaluationResponse with results
        """
        if self.runner is None:
            from cloudmigration_benchmark import BenchmarkRunner
            self.runner = BenchmarkRunner()

        # Load test suite
        self.runner.load_test_suite(request.test_suite_path)

        # Run evaluation
        report = self.runner.run_evaluation(
            dimensions=request.dimensions,
            max_samples=request.max_samples,
        )

        # Return response
        return EvaluationResponse(
            status="completed",
            report_id=f"rpt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            results=report.to_dict(),
            summary={
                "overall_score": report.overall_score,
                "pass_rate": report.pass_rate,
                "total_tests": report.total_tests,
            },
        )

    def _reports(self, report_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get evaluation reports.

        Args:
            report_id: Optional specific report ID

        Returns:
            Report data or list of reports
        """
        # Placeholder for report retrieval
        return {"reports": [], "count": 0}

    def _test_suites(self) -> Dict[str, Any]:
        """
        List available test suites.

        Returns:
            List of available test suite metadata
        """
        return {"test_suites": [], "count": 0}

    def to_dict(self) -> Dict[str, Any]:
        """Convert API info to dictionary."""
        return {
            "name": "CloudMigration-Benchmark-API",
            "version": "0.1.0",
            "endpoints": list(self.routes.keys()),
        }


def create_api_spec() -> Dict[str, Any]:
    """
    Create OpenAPI specification for the API.

    Returns:
        OpenAPI specification dictionary
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "CloudMigration Benchmark API",
            "version": "0.1.0",
            "description": "REST API for AI Agent evaluation in cloud migration scenarios",
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "Healthy"}},
                }
            },
            "/evaluate": {
                "post": {
                    "summary": "Run evaluation",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/EvaluationRequest"
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "Evaluation completed"}},
                }
            },
        },
        "components": {
            "schemas": {
                "EvaluationRequest": {
                    "type": "object",
                    "properties": {
                        "test_suite_path": {"type": "string"},
                        "dimensions": {"type": "array", "items": {"type": "string"}},
                        "max_samples": {"type": "integer"},
                    },
                }
            }
        },
    }