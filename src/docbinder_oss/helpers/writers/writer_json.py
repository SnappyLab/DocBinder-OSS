import json
from pathlib import Path
from typing import Dict, List, Union
from docbinder_oss.core.schemas import File
from docbinder_oss.helpers.writers.base import Writer


class JSONWriter(Writer):
    """Writer for exporting data to JSON files."""

    def write(self, data: Dict[str, List[File]], file_path: Union[str, Path]) -> None:
        data = {
            provider: [item.model_dump() for item in items]
            for provider, items in data.items()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
