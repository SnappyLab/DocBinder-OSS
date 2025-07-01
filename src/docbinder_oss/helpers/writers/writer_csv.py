import csv
import logging
from pathlib import Path
from typing import List, Dict, Union
from pydantic import BaseModel
from docbinder_oss.helpers.writers.base import Writer

logger = logging.getLogger(__name__)


class CSVWriter(Writer):
    """Writer for exporting data to CSV files."""
    def get_fieldnames(self, data: Dict[str, List[BaseModel]]) -> List[str]:
        fieldnames = next(iter(data.values()))[0].model_fields_set
        return ["provider", *fieldnames]

    def write(self, data: List[Dict], file_path: Union[str, Path]) -> None:
        if not data:
            logger.warning("No data to write to CSV.")
            return

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_fieldnames(data))
            writer.writeheader()
            for provider, items in data.items():
                for item in items:
                    item_dict = item.model_dump() if isinstance(item, BaseModel) else item
                    item_dict['provider'] = provider
                    writer.writerow(item_dict)
