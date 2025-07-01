import csv
import json
from typing import Dict
import pytest
from pathlib import Path
from typer.testing import CliRunner
from docbinder_oss.core.schemas import User
from docbinder_oss.main import app
from conftest import DummyModel


runner = CliRunner()

@pytest.mark.parametrize('load_config_mock', [("dummy", 2)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file"),
            ])], indirect=True)
def test_search_export_csv(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test happy path for search command with CSV export."""
    result = runner.invoke(app, ["search", "--export-file", "search_results.csv"])
    assert result.exit_code == 0
    assert Path("search_results.csv").exists()
    with open("search_results.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 4
        assert set(r["provider"] for r in rows) == {"dummy1", "dummy2"}

@pytest.mark.parametrize('load_config_mock', [("dummy", 2)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file"),
            ])], indirect=True)
def test_search_export_json(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test happy path for search command with CSV export."""
    result = runner.invoke(app, ["search", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    assert Path("search_results.json").exists()
    with open("search_results.json") as f:
        data: Dict = json.load(f)
        assert len(data.keys()) == 2
        assert len(data["dummy1"]) == 2
        assert len(data["dummy2"]) == 2
        assert all(key in data for key in ("dummy1", "dummy2"))

@pytest.mark.parametrize('load_config_mock', [("dummy", 2)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file"),
            ])], indirect=True)
def test_search_name_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """
    Test search command with name filter that returns no results.
    """
    result = runner.invoke(app, ["search", "--name", "Alpha", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 0
        assert len(data["dummy2"]) == 0
        
@pytest.mark.parametrize('load_config_mock', [("dummy", 2)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file"),
                DummyModel(id="dummy_file2", name="File 2", kind="file"),
            ])], indirect=True)
def test_search_name_filter_not_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """
    Test search command with name filter that returns some results.
    """
    result = runner.invoke(app, ["search", "--name", "dummy", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 2
        assert data["dummy1"][0]["name"] == "dummy File 1"
        assert data["dummy2"][0]["name"] == "dummy File 1"

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(
                    id="dummy_file1",
                    name="dummy File 1",
                    kind="file",
                    owners=[
                        User(
                            display_name="test",
                            email_address="beta@a.com",
                            photo_link="https://test.com",
                            kind=""
                        )
                    ]
                ),
                DummyModel(id="dummy_file2", name="File 2", kind="file", owners=[]),
            ])], indirect=True)
def test_search_owner_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with owner filter that returns no results."""
    result = runner.invoke(app, ["search", "--owner", "beta@b.com", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 0

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(
                    id="dummy_file1",
                    name="dummy File 1",
                    kind="file",
                    owners=[
                        User(
                            display_name="test",
                            email_address="beta@b.com",
                            photo_link="https://test.com",
                            kind=""
                        )
                    ]
                ),
                DummyModel(id="dummy_file2", name="File 2", kind="file", owners=[]),
            ])], indirect=True)
def test_search_owner_filter_not_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with owner filter that returns some results."""
    result = runner.invoke(app, ["search", "--owner", "beta@b.com", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data["dummy1"][0]["owners"][0]["email_address"] == "beta@b.com"

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", modified_time="2023-02-02T00:00:00"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", modified_time="2024-01-31T00:00:00"),
            ])], indirect=True)   
def test_search_updated_after_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with updated_after filter that returns no results."""
    result = runner.invoke(app, ["search", "--updated-after", "2024-02-01T00:00:00", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 0
        
@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", modified_time="2024-02-02T00:00:00"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", modified_time="2024-01-31T00:00:00"),
            ])], indirect=True)   
def test_search_updated_after_filter_not_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with updated_after filter that returns some results."""
    result = runner.invoke(app, ["search", "--updated-after", "2024-02-01T00:00:00", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 1
        assert data["dummy1"][0]["name"] == "dummy File 1"

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", created_time="2024-04-02T00:00:00"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", created_time="2024-04-30T00:00:00"),
            ])], indirect=True)  
def test_search_created_before_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with created_before filter that returns no results."""
    result = runner.invoke(
        app, ["search", "--created-before", "2024-02-01T00:00:00", "--export-file", "search_results.json"]
    )
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 0

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", created_time="2024-02-02T00:00:00"),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", created_time="2024-01-31T00:00:00"),
            ])], indirect=True)  
def test_search_created_before_filter_not_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with created_before filter that returns some results."""
    result = runner.invoke(
        app, ["search", "--created-before", "2024-02-01T00:00:00", "--export-file", "search_results.json"]
    )
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 1
        assert data["dummy1"][0]["name"] == "dummy File 2"

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", size=1),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=2),
            ])], indirect=True)  
def test_search_min_size_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with min_size filter that returns no results."""
    result = runner.invoke(app, ["search", "--min-size", 3, "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 0

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", size=5),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=2),
            ])], indirect=True) 
def test_search_min_size_filter_not_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--min-size", 3, "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 1
        assert data["dummy1"][0]["name"] == "dummy File 1"

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", size=5),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=3),
            ])], indirect=True) 
def test_search_max_size_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with max_size filter that returns no results."""
    result = runner.invoke(app, ["search", "--max-size", "3", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 1

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", size=5),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=2),
            ])], indirect=True) 
def test_search_max_size_filter_not_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with max_size filter that returns some results."""
    result = runner.invoke(app, ["search", "--max-size", "3", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data["dummy1"]) == 1
        assert data["dummy1"][0]["name"] == "dummy File 2"

@pytest.mark.parametrize('load_config_mock', [("dummy", 1)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", size=5),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=2),
            ])], indirect=True) 
def test_search_provider_filter_empty(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with provider filter that returns no results."""
    result = runner.invoke(app, ["search", "--provider", "dummy2", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 0

@pytest.mark.parametrize('load_config_mock', [("dummy", 2)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(id="dummy_file1", name="dummy File 1", kind="file", size=5),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=2),
            ])], indirect=True) 
def test_search_provider_filter(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with provider filter that returns some results."""
    result = runner.invoke(app, ["search", "--provider", "dummy2", "--export-file", "search_results.json"])
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert "dummy2" in data

@pytest.mark.parametrize('load_config_mock', [("dummy", 2)], indirect=True)
@pytest.mark.parametrize('create_provider_instance_mock', [("dummy")], indirect=True)
@pytest.mark.parametrize('list_all_files_mock', [([
                DummyModel(
                    id="dummy_file1",
                    name="Beta File 1",
                    kind="file",
                    size=5,
                    owners=[
                        User(
                            display_name="test",
                            email_address="beta@b.com",
                            photo_link="https://test.com",
                            kind=""
                        )
                    ]
                ),
                DummyModel(id="dummy_file2", name="dummy File 2", kind="file", size=2),
            ])], indirect=True) 
def test_search_combined_filters(load_config_mock, create_provider_instance_mock, list_all_files_mock):
    """Test search command with combined filters."""
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
            "--export-file",
            "search_results.json",
        ],
    )
    assert result.exit_code == 0
    with open("search_results.json") as f:
        data = json.load(f)
        assert len(data) == 1
        assert "dummy2" in data
        assert data["dummy2"][0]["name"] == "Beta File 1"
        assert data["dummy2"][0]["owners"][0]["email_address"] == "beta@b.com"
