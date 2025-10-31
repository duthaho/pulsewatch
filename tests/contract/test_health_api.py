"""
Contract tests for health check API.

Validates that API responses match the OpenAPI schema defined in
contracts/health.yaml.
"""

import re
from datetime import datetime

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.contract
@pytest.mark.django_db
class TestHealthAPIContracts:
    """Contract tests validating health API against OpenAPI spec."""

    def test_healthz_response_schema(self, api_client: APIClient) -> None:
        """
        Test that /healthz response matches LivenessResponse schema.

        Required fields:
        - status: string (enum: healthy, unhealthy)
        - timestamp: string (ISO 8601 date-time)
        - version: string (semver pattern: x.y.z)
        """
        url = reverse("healthz")
        response = api_client.get(url)

        # Verify required fields exist
        assert "status" in response.data
        assert "timestamp" in response.data
        assert "version" in response.data

        # Verify field types and formats
        assert isinstance(response.data["status"], str)
        assert response.data["status"] in ["healthy", "unhealthy"]

        # Verify timestamp is valid ISO 8601
        assert isinstance(response.data["timestamp"], str)
        self._validate_iso8601_timestamp(response.data["timestamp"])

        # Verify version matches semver pattern (x.y.z)
        assert isinstance(response.data["version"], str)
        self._validate_semver(response.data["version"])

    def test_ready_response_schema_when_healthy(self, api_client: APIClient) -> None:
        """
        Test that /ready response matches ReadinessResponse schema when healthy.

        Required fields:
        - status: string (enum: ready, not_ready)
        - timestamp: string (ISO 8601 date-time)
        - version: string (semver pattern: x.y.z)
        - checks: object (map of HealthCheckResult)
        """
        url = reverse("ready")
        response = api_client.get(url)

        # Verify required top-level fields
        assert "status" in response.data
        assert "timestamp" in response.data
        assert "version" in response.data
        assert "checks" in response.data

        # Verify status field
        assert isinstance(response.data["status"], str)
        assert response.data["status"] in ["ready", "not_ready"]

        # Verify timestamp
        assert isinstance(response.data["timestamp"], str)
        self._validate_iso8601_timestamp(response.data["timestamp"])

        # Verify version
        assert isinstance(response.data["version"], str)
        self._validate_semver(response.data["version"])

        # Verify checks is a dict
        assert isinstance(response.data["checks"], dict)

        # Verify database check exists and matches HealthCheckResult schema
        assert "database" in response.data["checks"]
        self._validate_health_check_result(response.data["checks"]["database"])

        # Verify redis check exists and matches HealthCheckResult schema
        assert "redis" in response.data["checks"]
        self._validate_health_check_result(response.data["checks"]["redis"])

    def test_ready_response_schema_when_unhealthy(self, api_client: APIClient, monkeypatch) -> None:
        """
        Test that /ready response matches ReadinessResponse schema when unhealthy.

        Validates the 503 response structure matches the contract.
        """

        # Mock database check to simulate failure
        def mock_db_check():
            return {
                "status": "unhealthy",
                "latency_ms": 5000.0,
                "message": "Database connection failed: Connection refused",
            }

        # Monkeypatch the function where it's used
        monkeypatch.setattr("core.health.views.database_health_check", mock_db_check)

        url = reverse("ready")
        response = api_client.get(url)

        # Verify HTTP 503 status
        assert response.status_code == 503

        # Verify response structure matches schema
        assert response.data["status"] == "not_ready"
        assert "timestamp" in response.data
        assert "version" in response.data
        assert "checks" in response.data

        # Verify unhealthy check structure
        db_check = response.data["checks"]["database"]
        assert db_check["status"] == "unhealthy"
        assert isinstance(db_check["latency_ms"], (int, float))
        assert db_check["latency_ms"] > 0
        assert isinstance(db_check["message"], str)

    def test_healthz_content_type_is_json(self, api_client: APIClient) -> None:
        """
        Test that /healthz returns application/json content type.

        Per OpenAPI spec, all responses must be application/json.
        """
        url = reverse("healthz")
        response = api_client.get(url)

        assert response["Content-Type"].startswith("application/json")

    def test_ready_content_type_is_json(self, api_client: APIClient) -> None:
        """
        Test that /ready returns application/json content type.

        Per OpenAPI spec, all responses must be application/json.
        """
        url = reverse("ready")
        response = api_client.get(url)

        assert response["Content-Type"].startswith("application/json")

    def test_health_check_result_latency_is_non_negative(self, api_client: APIClient) -> None:
        """
        Test that latency_ms in HealthCheckResult is non-negative.

        Per schema: latency_ms must be >= 0
        """
        url = reverse("ready")
        response = api_client.get(url)

        for check_name, check_result in response.data["checks"].items():
            assert check_result["latency_ms"] >= 0, (
                f"{check_name} check has negative latency: " f"{check_result['latency_ms']}"
            )

    # Helper methods for validation

    def _validate_iso8601_timestamp(self, timestamp_str: str) -> None:
        """
        Validate that string is valid ISO 8601 timestamp.

        Accepts formats like:
        - 2025-10-31T10:30:00.123456Z
        - 2025-10-31T10:30:00Z
        - 2025-10-31T10:30:00+00:00
        """
        try:
            # Try parsing with fromisoformat (Python 3.11+)
            datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pytest.fail(f"Invalid ISO 8601 timestamp: {timestamp_str}")

    def _validate_semver(self, version_str: str) -> None:
        """
        Validate that string matches semantic versioning pattern (x.y.z).

        Pattern: ^\\d+\\.\\d+\\.\\d+$
        """
        pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(
            pattern, version_str
        ), f"Version '{version_str}' does not match semver pattern x.y.z"

    def _validate_health_check_result(self, check_result: dict) -> None:
        """
        Validate that dict matches HealthCheckResult schema.

        Required fields:
        - status: string (enum: healthy, unhealthy, degraded)
        - latency_ms: number (>= 0)
        - message: string
        """
        # Verify required fields
        assert "status" in check_result
        assert "latency_ms" in check_result
        assert "message" in check_result

        # Verify field types and constraints
        assert isinstance(check_result["status"], str)
        assert check_result["status"] in ["healthy", "unhealthy", "degraded"]

        assert isinstance(check_result["latency_ms"], (int, float))
        assert check_result["latency_ms"] >= 0

        assert isinstance(check_result["message"], str)
        assert len(check_result["message"]) > 0
