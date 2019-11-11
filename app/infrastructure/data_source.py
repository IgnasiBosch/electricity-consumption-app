import asyncio
import logging
import operator

from aiohttp import ClientError

from app.usecase.entities import DataCollection, DataItem, DataResult


class DataSource:
    """Datasource behaves similar as a repository, it provides the data from the
    external world"""

    _interval_after_error = 300

    def __init__(self, client):
        self.client = client
        self._energy_consumption_per_capita: DataResult = DataResult("", 0, [])
        self._electricity_access_ranking: DataResult = DataResult("", 0, [])

    async def _update_energy_consumption(self):
        """Fetches needed data to compute the energy consumption per capita and
        store it in memory"""

        logging.log(logging.INFO, "Updating energy consumption data...")
        total_consumption = await self.client.get_latest_energy_consumption()
        total_population = await self.client.get_country_population_by_year(
            total_consumption.year
        )

        self._energy_consumption_per_capita = self.calculate_energy_consumption_per_capita(
            total_consumption, total_population
        )
        logging.log(logging.INFO, "Energy consumption data updated")

    async def _update_electricity_access_ranking(self):
        """Fetches and store in memory the electricity access data"""
        logging.log(logging.INFO, "Updating electricity access data...")
        result: DataCollection = await self.client.get_latest_electricity_access()

        self._electricity_access_ranking = DataResult(
            indicator="Access to electricity (% of total population)",
            year=result.year,
            items=sorted(
                (i for i in result.items.values() if i.value is not None),
                key=operator.attrgetter("value"),
                reverse=True,
            ),
        )
        logging.log(logging.INFO, "Electricity access data updated")

    async def update_values(self):
        """Updates the in-memory data asynchronously"""
        try:
            await asyncio.gather(
                self._update_energy_consumption(),
                self._update_electricity_access_ranking(),
            )
        except ClientError:
            return False
        else:
            return True

    async def update_task(self, *, interval_in_days) -> None:
        """Task to run periodically as a background task"""
        interval = 3600 * 24 * interval_in_days

        await asyncio.sleep(interval)
        while True:
            success = await self.update_values()
            await asyncio.sleep(interval if success else self._interval_after_error)

    def energy_consumption_per_capita(self, limit: int) -> DataResult:
        return DataResult(
            indicator=self._energy_consumption_per_capita.indicator,
            year=self._energy_consumption_per_capita.year,
            items=self._energy_consumption_per_capita.items[:limit],
        )

    def energy_consumption_per_capita_by_country(self, country_name: str) -> DataResult:
        return DataResult(
            indicator=self._energy_consumption_per_capita.indicator,
            year=self._energy_consumption_per_capita.year,
            items=[
                item
                for item in self._energy_consumption_per_capita.items
                if item.label.lower() == country_name.lower()
            ],
        )

    def electricity_access_ranking(
        self, limit: int, bottom: bool = False
    ) -> DataResult:
        items = (
            self._electricity_access_ranking.items[:limit]
            if not bottom
            else self._electricity_access_ranking.items[-limit:]
        )
        return DataResult(
            indicator=self._electricity_access_ranking.indicator,
            year=self._electricity_access_ranking.year,
            items=items,
        )

    def electricity_ranking_by_country(self, country_name: str):
        return DataResult(
            indicator=self._electricity_access_ranking.indicator,
            year=self._electricity_access_ranking.year,
            items=[
                item
                for item in self._electricity_access_ranking.items
                if item.label.lower() == country_name.lower()
            ],
        )

    @classmethod
    def calculate_energy_consumption_per_capita(
        cls, total_consumption: DataCollection, total_population: DataCollection
    ) -> DataResult:
        """Total energy consumption from a country divided by total population"""
        common_countries = set(total_consumption.items.keys()).intersection(
            set(total_population.items.keys())
        )

        items = []

        for country in common_countries:
            try:
                item = DataItem(
                    label=country,
                    value=cls.safe_div(total_consumption, total_population, country),
                )
            except ValueError:
                continue  # prioritizes returning result rather than fail
            else:
                items.append(item)

        return DataResult(
            indicator="Total Energy Consumption per capita",
            year=total_consumption.year,
            items=sorted(items, key=operator.attrgetter("value"), reverse=True),
        )

    @staticmethod
    def safe_div(
        total_consumption: DataCollection,
        total_population: DataCollection,
        country: str,
    ):
        """As some of the provided data might contain None values we need a safe
        way to compute the values"""

        dividend = total_consumption.get_value_by_label(country)
        divisor = total_population.get_value_by_label(country)

        if dividend and divisor:
            return dividend / divisor

        raise ValueError("Not feasible to proceed with the operation")
