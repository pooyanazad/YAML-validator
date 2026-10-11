"""Regression tests for release/version and publication guards."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

from scripts import pypi_status, release_plan


@pytest.fixture(autouse=True)
def version():
    with patch.object(release_plan, "package_version", return_value="3.5.0"):
        yield


def test_new_release_uses_package_version():
    with patch.object(release_plan, "previous_tag", return_value="v3.4.0-20261011"):
        result = release_plan.plan("HEAD", "workflow_dispatch", "", ["v3.4.0-20261011"], "20261012")
    assert result == {
        "version": "v3.5.0-20261012",
        "package_version": "3.5.0",
        "latest_tag": "v3.4.0-20261011",
        "publish_release": "true",
    }


@pytest.mark.parametrize("tag", ["v3.6.0-20261012", "v3.5.0-20260230", "main", "--help"])
def test_bad_manual_tag_cannot_publish(tag):
    with pytest.raises(ValueError):
        release_plan.plan("HEAD", "workflow_dispatch", tag, [], "20261012")


def test_second_date_does_not_create_second_package_release():
    with pytest.raises(ValueError, match="already has"):
        release_plan.plan("HEAD", "workflow_dispatch", "", ["v3.5.0-20261011"], "20261101")


def test_monthly_rebuild_only_refreshes_latest():
    with patch.object(
        release_plan, "previous_tag", side_effect=AssertionError("must not plan a release")
    ):
        result = release_plan.plan("HEAD", "schedule", "", ["v3.5.0-20261011"], "20261101")
    assert result["publish_release"] == "false"


@pytest.mark.parametrize("event", ["push", "pull_request"])
def test_ci_never_publishes_or_fails_on_existing_release(event):
    with patch.object(
        release_plan, "previous_tag", side_effect=AssertionError("CI is not a release")
    ):
        assert (
            release_plan.plan("HEAD", event, "", ["v3.5.0-20261011"], "20261011")["publish_release"]
            == "false"
        )


def test_release_cannot_downgrade_latest():
    with pytest.raises(ValueError, match="downgrade"):
        release_plan.plan("HEAD", "schedule", "", ["v3.6.0-20261101"], "20261201")


def test_only_pypi_404_means_unpublished():
    with patch.object(
        pypi_status, "urlopen", side_effect=HTTPError("url", 404, "missing", {}, None)
    ):
        assert not pypi_status.is_published("3.5.0")


@pytest.mark.parametrize(
    "error", [HTTPError("url", 503, "unavailable", {}, None), URLError("offline")]
)
def test_pypi_errors_are_not_treated_as_missing(error):
    with patch.object(pypi_status, "urlopen", side_effect=error), pytest.raises(type(error)):
        pypi_status.is_published("3.5.0")


def test_existing_pypi_version_is_skipped():
    response = MagicMock()
    response.__enter__.return_value.read.return_value = b'{"info":{"version":"3.5.0"},"urls":[{}]}'
    with patch.object(pypi_status, "urlopen", return_value=response):
        assert pypi_status.is_published("3.5.0")


def test_empty_pypi_version_needs_inspection():
    response = MagicMock()
    response.__enter__.return_value.read.return_value = b'{"info":{"version":"3.5.0"},"urls":[]}'
    with (
        patch.object(pypi_status, "urlopen", return_value=response),
        pytest.raises(ValueError, match="without files"),
    ):
        pypi_status.is_published("3.5.0")
