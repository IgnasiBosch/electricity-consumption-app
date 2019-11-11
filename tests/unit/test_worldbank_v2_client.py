import copy

import pytest
from asynctest import CoroutineMock

from app.infrastructure.http.clients import WorldBankV2Client
from app.usecase.entities import DataItem


@pytest.fixture
def wb_client(mocker):
    return WorldBankV2Client(mocker.Mock(), "http://example.com")


def test_to_item_mapper():
    data = {
        "indicator": {
            "id": "1.1_ACCESS.ELECTRICITY.TOT",
            "value": "Access to electricity (% of total population)",
        },
        "country": {"id": "NRU", "value": "Nauru"},
        "countryiso3code": "",
        "date": "2015",
        "value": 99,
        "unit": "",
        "obs_status": "",
        "decimal": 2,
    }

    expected_result = DataItem(label="Nauru", value=99)

    result = WorldBankV2Client.to_item(data)

    assert expected_result == result


@pytest.mark.asyncio
async def test_get_all_pagination(wb_client):
    first_page = [
        [
            {
                "page": 1,
                "pages": 3,
                "per_page": 3,
                "total": 9,
                "sourceid": "35",
                "lastupdated": "2018-06-30",
            },
            [
                {
                    "indicator": {
                        "id": "1.1_ACCESS.ELECTRICITY.TOT",
                        "value": "Access to electricity (% of total population)",
                    },
                    "country": {"id": "BES", "value": "BES Islands"},
                    "countryiso3code": "",
                    "date": "2016",
                    "value": None,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2,
                },
                {
                    "indicator": {
                        "id": "1.1_ACCESS.ELECTRICITY.TOT",
                        "value": "Access to electricity (% of total population)",
                    },
                    "country": {"id": "BES", "value": "BES Islands"},
                    "countryiso3code": "",
                    "date": "2015",
                    "value": None,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2,
                },
                {
                    "indicator": {
                        "id": "1.1_ACCESS.ELECTRICITY.TOT",
                        "value": "Access to electricity (% of total population)",
                    },
                    "country": {"id": "BES", "value": "BES Islands"},
                    "countryiso3code": "",
                    "date": "2014",
                    "value": None,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2,
                },
            ],
        ]
    ]

    wb_client._http_client.get = CoroutineMock()

    second_page = copy.deepcopy(first_page)
    second_page[0][0]["page"] = 2

    third_page = copy.deepcopy(first_page)
    third_page[0][0]["page"] = 3

    wb_client._http_client.get.side_effect = [first_page, [second_page, third_page]]

    async_gen = wb_client._get_all(wb_client.url.format("/test"))

    result_first_page = await async_gen.__anext__()
    result_second_page = await async_gen.__anext__()
    result_third_page = await async_gen.__anext__()

    assert first_page[0] == result_first_page
    assert second_page == result_second_page
    assert third_page == result_third_page
