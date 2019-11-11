from unittest.mock import call

from app.usecase.electricity_access import electricity_access
from app.usecase.entities import DataResult, DataItem


def test_use_case(mocker, data_results):
    mocked_ds = mocker.Mock()
    stub_by_country = DataResult(
        indicator="Total Energy Consumption per capita",
        year=None,
        items=[DataItem(label="Austria", value=0.10661932078144108)],
    )

    mocked_ds.electricity_access_ranking.return_value = data_results
    mocked_ds.electricity_ranking_by_country.return_value = stub_by_country

    result = electricity_access(mocked_ds, "Austria", 10)

    mocked_ds.electricity_access_ranking.mock_calls = [call(10), call(10, bottom=True)]
    mocked_ds.electricity_ranking_by_country.assert_called_once_with("Austria")

    assert 1 == len([i for i in result[0].items if i.label == "Austria"])
