import os
import csv
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
        self.owners = kwargs.get("owners", [type("User", (), {"email_address": "owner@example.com"})()])
        self.last_modifying_user = kwargs.get(
            "last_modifying_user", type("User", (), {"email_address": "mod@example.com"})()
        )
        self.web_view_link = kwargs.get("web_view_link", "http://example.com/view")
        self.web_content_link = kwargs.get("web_content_link", "http://example.com/content")
        self.shared = kwargs.get("shared", True)
        self.trashed = kwargs.get("trashed", False)

    def model_dump(self):
        # Simulate pydantic's model_dump for test compatibility
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "mime_type": self.mime_type,
            "created_time": self.created_time,
            "modified_time": self.modified_time,
            "owners": [u.email_address for u in self.owners],
            "last_modifying_user": getattr(self.last_modifying_user, "email_address", None),
            "web_view_link": self.web_view_link,
            "web_content_link": self.web_content_link,
            "shared": self.shared,
            "trashed": self.trashed,
        }


@pytest.fixture(autouse=True)
def patch_provider(monkeypatch, tmp_path):
    # Patch config loader to return two dummy provider configs
    class DummyProviderConfig:
        def __init__(self, name):
            self.name = name
            self.type = name  # Simulate type for registry

    class DummyConfig:
        providers = [DummyProviderConfig("dummy1"), DummyProviderConfig("dummy2")]

    # Patch load_config in the CLI's namespace
    monkeypatch.setattr("docbinder_oss.cli.search.load_config", lambda: DummyConfig())

    # Patch create_provider_instance in the CLI's namespace
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

    monkeypatch.setattr("docbinder_oss.cli.search.create_provider_instance", create_provider_instance)

    # Change working directory to a temp dir for file output
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(orig_cwd)


def test_search_export_csv():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--export-format", "csv"])
    assert result.exit_code == 0
    assert os.path.exists("search_results.csv")
    with open("search_results.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        names = set(r["name"] for r in rows)
        assert names == {"Alpha Report", "Beta Notes"}
        # Check owners field is a string and contains the expected email
        for r in rows:
            owners = r["owners"]
            if r["name"] == "Alpha Report":
                assert "alpha@a.com" in owners
            if r["name"] == "Beta Notes":
                assert "beta@b.com" in owners


def test_search_export_json():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--export-format", "json"])
    assert result.exit_code == 0
    assert os.path.exists("search_results.json")
    with open("search_results.json") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 2
        names = set(d["name"] for d in data)
        assert names == {"Alpha Report", "Beta Notes"}
        # Check owners field is a string or list
        for d in data:
            if d["name"] == "Alpha Report":
                assert "alpha@a.com" in d["owners"]
            if d["name"] == "Beta Notes":
                assert "beta@b.com" in d["owners"]


def test_search_name_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--name", "Alpha", "--export-format", "json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Alpha Report"


def test_search_owner_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--owner", "beta@b.com", "--export-format", "json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Beta Notes"


def test_search_updated_after_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--updated-after", "2024-02-01T00:00:00", "--export-format", "json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["name"] == "Beta Notes"


def test_search_created_before_filter():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--created-before", "2024-02-01T00:00:00", "--export-format", "json"])
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
        assert "beta@b.com" in data[0]["owners"]
