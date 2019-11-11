import pytest
from asynctest import CoroutineMock

from app.infrastructure.data_source import DataSource
from app.usecase.entities import DataResult, DataItem, DataCollection


@pytest.fixture
def stub_data_source(mocker, data_results):
    stub_ds = DataSource(mocker.Mock())
    stub_ds._energy_consumption_per_capita = data_results
    stub_ds._electricity_access_ranking = data_results
    return stub_ds


def test_ds_electricity_access_ranking(stub_data_source):

    result_top = stub_data_source.electricity_access_ranking(3)
    result_bottom = stub_data_source.electricity_access_ranking(3, True)

    assert 3 == len(result_top.items)
    assert result_bottom != result_top


def test_ds_electricity_ranking_by_country(stub_data_source):

    result = stub_data_source.electricity_ranking_by_country("Andorra")

    assert 1 == len(result.items)
    assert result.items[0].label == "Andorra"


def test_ds_electricity_ranking_by_country_case_insensitive(stub_data_source):

    result = stub_data_source.electricity_ranking_by_country("andorra")

    assert 1 == len(result.items)
    assert result.items[0].label == "Andorra"


def test_ds_electricity_ranking_by_country_missing(stub_data_source):

    result = stub_data_source.electricity_ranking_by_country("Neverland")

    assert 0 == len(result.items)


def test_ds_energy_consumption_per_capita(stub_data_source):

    result = stub_data_source.energy_consumption_per_capita(3)

    assert 3 == len(result.items)


def test_ds_energy_consumption_per_capita_by_country(stub_data_source):

    result = stub_data_source.energy_consumption_per_capita_by_country("Afghanistan")

    assert 1 == len(result.items)
    assert result.items[0].label == "Afghanistan"


def test_ds_energy_consumption_per_capita_by_country_case_insensitive(stub_data_source):

    result = stub_data_source.energy_consumption_per_capita_by_country("afghanistan")

    assert 1 == len(result.items)
    assert result.items[0].label == "Afghanistan"


def test_ds_energy_consumption_per_capita_by_country_missing(stub_data_source):

    result = stub_data_source.energy_consumption_per_capita_by_country("Neverland")

    assert 0 == len(result.items)


@pytest.mark.asyncio
async def test_update_electricity_access_ranking(
    stub_data_source, electricity_access_data
):
    stub_data_source.client.get_latest_electricity_access = CoroutineMock()

    stub_data_source.client.get_latest_electricity_access.return_value = (
        electricity_access_data
    )

    await stub_data_source._update_electricity_access_ranking()

    stub_data_source.client.get_latest_electricity_access.assert_awaited_once()

    expected_value = DataResult(
        indicator="Access to electricity (% of total population)",
        year=None,
        items=[
            DataItem(label="Albania", value=100),
            DataItem(label="Andorra", value=100),
            DataItem(label="Belize", value=100),
            DataItem(label="Algeria", value=99.439567565918),
            DataItem(label="Benin", value=98.65456764),
            DataItem(label="Bermuda", value=89.877655),
            DataItem(label="Afghanistan", value=84.1371383666992),
            DataItem(label="Bhutan", value=76.543433),
            DataItem(label="American Samoa", value=45.4345565),
        ],
    )
    assert stub_data_source._electricity_access_ranking == expected_value


@pytest.mark.asyncio
async def test_update_energy_consumption(
    stub_data_source, consumption_data, population_data
):
    stub_data_source.client.get_latest_energy_consumption = CoroutineMock()
    stub_data_source.client.get_country_population_by_year = CoroutineMock()

    stub_data_source.client.get_latest_energy_consumption.return_value = (
        consumption_data
    )

    stub_data_source.client.get_country_population_by_year.return_value = (
        population_data
    )

    await stub_data_source._update_energy_consumption()

    stub_data_source.client.get_latest_energy_consumption.assert_awaited_once()
    stub_data_source.client.get_country_population_by_year.assert_awaited_once_with(
        2019
    )

    expected_value = DataResult(
        indicator="Total Energy Consumption per capita",
        year=2019,
        items=[
            DataItem(label="Andorra", value=0.10661932078144108),
            DataItem(label="Bhutan", value=0.08634059819254929),
            DataItem(label="Bermuda", value=0.08014185683410231),
            DataItem(label="Algeria", value=0.03559174751717459),
            DataItem(label="Belize", value=0.033856560433376835),
            DataItem(label="Albania", value=0.02836726636657788),
            DataItem(label="Benin", value=0.01421644368355681),
            DataItem(label="American Samoa", value=0.010052676843689528),
            DataItem(label="Afghanistan", value=0.003964322923699678),
        ],
    )

    assert stub_data_source._energy_consumption_per_capita == expected_value


def test_safe_div_fail():

    a = DataCollection(
        items={item.label: item for item in [DataItem(label="Albania", value=100)]}
    )

    b = DataCollection(
        items={item.label: item for item in [DataItem(label="Albania", value=None)]}
    )

    with pytest.raises(ValueError):
        DataSource.safe_div(a, b, "Albania")


def test_safe_div_succeed():

    a = DataCollection(
        items={item.label: item for item in [DataItem(label="Albania", value=2343)]}
    )

    b = DataCollection(
        items={item.label: item for item in [DataItem(label="Albania", value=200000)]}
    )

    result = DataSource.safe_div(a, b, "Albania")

    assert 0.011715 == result
