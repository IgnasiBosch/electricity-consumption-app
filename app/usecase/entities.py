from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DataItem:
    label: str
    value: Any


@dataclass
class DataCollection:
    items: Dict[str, DataItem]
    year: Optional[int] = None
    last_updated: Optional[str] = None

    def get_value_by_label(self, label: str) -> Optional[Any]:
        item = self.items.get(label)
        return item.value if item is not None else None


@dataclass(frozen=True)
class DataResult:
    indicator: str
    year: Optional[int]
    items: List[DataItem]
