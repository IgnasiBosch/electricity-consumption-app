"""
HTTP Clients

"""

import asyncio
from typing import AsyncIterator, Dict, List, Optional, Tuple

import aiohttp

from app.usecase.entities import DataCollection, DataItem


class HTTPClient:  # pylint: disable=too-few-public-methods
    """Uses a connection pool in order to optimize the connection management"""

    def __init__(self, client_session: Optional[aiohttp.ClientSession]):
        self._client_session = client_session or aiohttp.ClientSession()

    async def _get_request(self, url: str, valid_status: Tuple[int] = (200,)):
        """generic get method that executes one request"""

        async with self._client_session.get(url=url) as resp:
            if resp.status not in valid_status:
                raise aiohttp.ClientError(
                    f"Error: status {resp.status} when fetching {url}"
                )

            return await resp.json()

    async def get(self, urls: List[str], valid_status: Tuple[int] = (200,)):
        """This method allows to execute many requests (non-blocking) asynchronously"""

        tasks = [
            asyncio.create_task(self._get_request(url, valid_status)) for url in urls
        ]

        return await asyncio.gather(*tasks)


class WorldBankV2Client:
    """Client to interact with api.worldbank.org/v2/"""

    per_page = 100
    url_suffix = "/v2/country/all"
    indicators = {
        "energy_consumption": "/indicator/1.1_TOTAL.FINAL.ENERGY.CONSUM",
        "population": "/indicator/SP.POP.TOTL",
        "electricity_access": "/indicator/1.1_ACCESS.ELECTRICITY.TOT",
    }

    def __init__(self, http_client: HTTPClient, base_url: str):
        self._http_client = http_client
        self.url = f"{base_url}{self.url_suffix}{{}}?format=json"

    async def get(self, url: str, collection=None, mapper=None) -> DataCollection:
        mapper = mapper or self.to_item
        collection = collection or self.to_collection
        get_all_gen = self._get_all(url)
        meta, first_page = await get_all_gen.__anext__()

        results = [first_page]
        async for _, next_page in get_all_gen:
            results.append(next_page)

        return collection(first_page, mapper, meta, results)

    @staticmethod
    def to_collection(first_page, mapper, meta, results):
        """maps the result to a domain's data collection instance in order to decouple
        the format from the original source"""

        return DataCollection(
            items={item.label: item for item in map(mapper, sum(results, []))},
            year=int(first_page[0].get("date"))
            if first_page and first_page[0].get("date").isnumeric()
            else None,
            last_updated=meta.get("lastupdated"),
        )

    async def _get_all(self, url: str) -> AsyncIterator:
        """Fetches the first page first, after that creates as much urls as needed
        with the requests to the rest of the pages and execute them asynchronously"""

        current_page = 1
        paginated_url = f"{url}&per_page={self.per_page}&page={{}}"

        json_resp = await self._http_client.get([paginated_url.format(current_page)])
        current_page += 1

        yield json_resp[0]

        urls = []
        for page in range(current_page, json_resp[0][0]["pages"] + 1):
            urls.append(paginated_url.format(page))

        json_resps = await self._http_client.get(urls)
        for json_resp in json_resps:
            yield json_resp

    async def get_by_year(self, year: int, indicator: str):
        return await self.get(
            url=f"{self.url.format(self.indicators[indicator])}&date=YTD:{year}"
        )

    async def get_latest_values(self, indicator: str):
        return await self.get(
            url=f"{self.url.format(self.indicators[indicator])}&mrvnev=1"
        )

    async def get_latest_energy_consumption(self):
        return await self.get_latest_values("energy_consumption")

    async def get_latest_electricity_access(self):
        return await self.get_latest_values("electricity_access")

    async def get_country_population_by_year(self, year: int):
        return await self.get_by_year(year, "population")

    @staticmethod
    def to_item(result: Dict):
        return DataItem(label=result["country"]["value"], value=result["value"])
