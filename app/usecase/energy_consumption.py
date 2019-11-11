from typing import Optional

from app.infrastructure.data_source import DataSource
from app.usecase.entities import DataResult


def energy_consumption_per_capita(
    data_source: DataSource, current_country: Optional[str], limit: int
) -> DataResult:

    data_result = data_source.energy_consumption_per_capita(limit)
    countries = {item.label for item in data_result.items}

    if current_country and current_country not in countries:
        data_result = DataResult(
            indicator=data_result.indicator,
            year=data_result.year,
            items=data_result.items
            + data_source.energy_consumption_per_capita_by_country(
                current_country
            ).items,
        )

    return data_result
