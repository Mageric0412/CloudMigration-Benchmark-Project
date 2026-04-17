"""
API module for CloudMigration-Benchmark-Project.

This module provides REST API interfaces for the benchmark system,
allowing integration with external services and programmatic access.
"""

from cloudmigration_benchmark.api.routes import (
    BenchmarkAPI,
    HealthCheck,
    EvaluationRequest,
    EvaluationResponse,
)

__all__ = [
    "BenchmarkAPI",
    "HealthCheck",
    "EvaluationRequest",
    "EvaluationResponse",
]