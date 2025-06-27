import json
import csv
import pytest
from pydantic import BaseModel

from docbinder_oss.helpers.writer import (
    MultiFormatWriter,
    CSVWriter,
    JSONWriter,
)


class DummyModel(BaseModel):
    id: str
    name: str
    kind: str


@pytest.fixture
def sample_data():
    return {
        "provider1": [
            DummyModel(id="1", name="FileA", kind="file"),
            DummyModel(id="2", name="FolderB", kind="folder"),
        ],
        "provider2": [
            DummyModel(id="3", name="FileC", kind="file"),
        ],
    }


def test_csv_writer(tmp_path, sample_data):
    file_path = tmp_path / "output.csv"
    writer = CSVWriter()
    writer.write(sample_data, file_path)
    assert file_path.exists()
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3
        assert set(rows[0].keys()) == {"provider", "id", "name", "kind"}
        assert rows[0]["provider"] == "provider1"


def test_json_writer(tmp_path, sample_data):
    file_path = tmp_path / "output.json"
    writer = JSONWriter()
    writer.write(sample_data, file_path)
    assert file_path.exists()
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
        assert "provider1" in data
        assert isinstance(data["provider1"], list)
        assert data["provider1"][0]["id"] == "1"


def test_multiformat_writer_csv(tmp_path, sample_data):
    file_path = tmp_path / "test.csv"
    MultiFormatWriter.write(sample_data, file_path)
    assert file_path.exists()
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3


def test_multiformat_writer_json(tmp_path, sample_data):
    file_path = tmp_path / "test.json"
    MultiFormatWriter.write(sample_data, file_path)
    assert file_path.exists()
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
        assert "provider2" in data


def test_multiformat_writer_unsupported(tmp_path, sample_data):
    file_path = tmp_path / "test.unsupported"
    with pytest.raises(ValueError):
        MultiFormatWriter.write(sample_data, file_path)


def test_csv_writer_empty_data(tmp_path, caplog):
    file_path = tmp_path / "empty.csv"
    writer = CSVWriter()
    with caplog.at_level("WARNING"):
        writer.write({}, file_path)
        assert "No data to write to CSV." in caplog.text
