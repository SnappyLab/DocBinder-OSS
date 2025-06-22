import os
import json
import pytest
from typer.testing import CliRunner
from docbinder_oss.main import app


class DummyFile:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "fileid1")
        self.name = kwargs.get("name", "Test File")
        self.size = kwargs.get("size", 12345)
        self.mime_type = kwargs.get("mime_type", "application/pdf")
        self.created_time = kwargs.get("created_time", "2024-01-01T00:00:00")
        self.modified_time = kwargs.get("modified_time", "2024-01-02T00:00:00")
        self.owners = kwargs.get(
            "owners", [type("User", (), {"email_address": "owner@example.com"})()]
        )
        self.last_modifying_user = kwargs.get(
            "last_modifying_user", type("User", (), {"email_address": "mod@example.com"})()
        )
        self.web_view_link = kwargs.get("web_view_link", "http://example.com/view")
        self.web_content_link = kwargs.get("web_content_link", "http://example.com/content")
        self.shared = kwargs.get("shared", True)
        self.trashed = kwargs.get("trashed", False)


@pytest.fixture(autouse=True)
def patch_provider(monkeypatch, tmp_path):
    # Patch config loader to return two dummy provider configs
    class DummyProviderConfig:
        def __init__(self, name):
            self.name = name

    class DummyConfig:
        providers = [DummyProviderConfig("dummy1"), DummyProviderConfig("dummy2")]

    monkeypatch.setattr("docbinder_oss.helpers.config.load_config", lambda: DummyConfig())

    # Patch create_provider_instance to return a dummy client with different files per provider
    def create_provider_instance(cfg):
        if cfg.name == "dummy1":
            return type(
                "DummyClient",
                (),
                {
                    "list_all_files": lambda self: [
                        DummyFile(
                            id="f1",
                            name="Alpha Report",
                            size=2048,
                            owners=[type("User", (), {"email_address": "alpha@a.com"})()],
                            created_time="2024-01-01T10:00:00",
                            modified_time="2024-01-02T10:00:00",
                        )
                    ]
                },
            )()
        else:
            return type(
                "DummyClient",
                (),
                {
                    "list_all_files": lambda self: [
                        DummyFile(
                            id="f2",
                            name="Beta Notes",
                            size=4096,
                            owners=[type("User", (), {"email_address": "beta@b.com"})()],
                            created_time="2024-02-01T10:00:00",
                            modified_time="2024-02-02T10:00:00",
                        )
                    ]
                },
            )()

    monkeypatch.setattr("docbinder_oss.services.create_provider_instance", create_provider_instance)
    # Change working directory to a temp dir for file output
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(orig_cwd)


# The test logic for search export and filters has been consolidated into
# `tests/commands/test_search_command.py`.
# This file no longer contains duplicate tests.
def test_search_updated_after_filter():
    runner = CliRunner()
    result = runner.invoke(
        app, ["search", "--updated-after", "2024-02-01T00:00:00", "--export-format", "json"]
    )
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Beta Notes"


def test_search_created_before_filter():
    runner = CliRunner()
    result = runner.invoke(
        app, ["search", "--created-before", "2024-02-01T00:00:00", "--export-format", "json"]
    )
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Alpha Report"


def test_search_min_size_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--min-size", "3", "--export-format", "json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Beta Notes"


def test_search_max_size_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--max-size", "3", "--export-format", "json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Alpha Report"


def test_search_provider_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--provider", "dummy2", "--export-format", "json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["provider"] == "dummy2"
        assert data[0]["name"] == "Beta Notes"


def test_search_combined_filters():
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "search",
            "--name",
            "Beta",
            "--owner",
            "beta@b.com",
            "--min-size",
            "3",
            "--provider",
            "dummy2",
            "--export-format",
            "json",
        ],
    )
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Beta Notes"
        assert data[0]["provider"] == "dummy2"
        assert data[0]["owners"] == "beta@b.com"
