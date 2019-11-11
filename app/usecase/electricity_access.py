from typing import Optional

from app.infrastructure.data_source import DataSource
from app.usecase.entities import DataResult


def electricity_access(
    data_source: DataSource, current_country: Optional[str], limit: int
):

    top = data_source.electricity_access_ranking(limit)
    bottom = data_source.electricity_access_ranking(limit, bottom=True)

    countries = {item.label for item in top.items + bottom.items}

    if current_country and current_country not in countries:
        top = DataResult(
            indicator=top.indicator,
            year=top.year,
            items=top.items
            + data_source.electricity_ranking_by_country(current_country).items,
        )

    return top, bottom
