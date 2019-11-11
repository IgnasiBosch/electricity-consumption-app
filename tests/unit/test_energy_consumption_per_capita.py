import pytest

from app.infrastructure.data_source import DataSource
from app.usecase.energy_consumption import energy_consumption_per_capita
from app.usecase.entities import DataItem, DataResult


def test_energy_consumption_per_capita(consumption_data, population_data):
    result = DataSource.calculate_energy_consumption_per_capita(
        consumption_data, population_data
    )

    first, second, third = result.items[:3]

    assert first.label == "Andorra"
    assert first.value == 0.10661932078144108

    assert second.label == "Bhutan"
    assert second.value == 0.08634059819254929

    assert third.label == "Bermuda"
    assert third.value == 0.08014185683410231


def test_energy_consumption_per_capita_skip_missing_population_item(
    consumption_data, population_data
):
    del population_data.items["Andorra"]

    result = DataSource.calculate_energy_consumption_per_capita(
        consumption_data, population_data
    )

    first, second, third = result.items[:3]

    assert first.label == "Bhutan"
    assert first.value == 0.08634059819254929

    assert second.label == "Bermuda"
    assert second.value == 0.08014185683410231

    assert third.label == "Algeria"
    assert third.value == 0.03559174751717459


def test_use_case(mocker, data_results):
    mocked_ds = mocker.Mock()
    stub_by_country = DataResult(
        indicator="Total Energy Consumption per capita",
        year=None,
        items=[DataItem(label="Austria", value=0.10661932078144108)],
    )

    mocked_ds.energy_consumption_per_capita.return_value = data_results
    mocked_ds.energy_consumption_per_capita_by_country.return_value = stub_by_country

    result = energy_consumption_per_capita(mocked_ds, "Austria", 10)

    mocked_ds.energy_consumption_per_capita.assert_called_once_with(10)
    mocked_ds.energy_consumption_per_capita_by_country.assert_called_once_with(
        "Austria"
    )

    assert 1 == len([i for i in result.items if i.label == "Austria"])
