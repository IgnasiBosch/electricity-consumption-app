import pytest

from app.usecase.entities import DataResult, DataItem, DataCollection


@pytest.fixture
def consumption_data():
    items = [
        DataItem(label="Afghanistan", value=136426.63526),
        DataItem(label="Albania", value=81717.669324),
        DataItem(label="Algeria", value=1413989.835156),
        DataItem(label="American Samoa", value=561.06),
        DataItem(label="Andorra", value=8317.479833481),
        DataItem(label="Belize", value=12219.9499269),
        DataItem(label="Benin", value=150352.426008),
        DataItem(label="Bermuda", value=5228.374598),
        DataItem(label="Bhutan", value=62845.24925),
    ]

    return DataCollection(year=2019, items={item.label: item for item in items})


@pytest.fixture
def population_data():
    items = [
        DataItem(label="Afghanistan", value=34413603),
        DataItem(label="Albania", value=2880703),
        DataItem(label="Algeria", value=39728025),
        DataItem(label="American Samoa", value=55812),
        DataItem(label="Andorra", value=78011),
        DataItem(label="Belize", value=360933),
        DataItem(label="Benin", value=10575952),
        DataItem(label="Bermuda", value=65239),
        DataItem(label="Bhutan", value=727876),
    ]

    return DataCollection(items={item.label: item for item in items})


@pytest.fixture
def electricity_access_data():
    items = [
        DataItem(label="Afghanistan", value=84.1371383666992),
        DataItem(label="Albania", value=100),
        DataItem(label="Algeria", value=99.439567565918),
        DataItem(label="American Samoa", value=45.4345565),
        DataItem(label="Andorra", value=100),
        DataItem(label="Belize", value=100),
        DataItem(label="Benin", value=98.65456764),
        DataItem(label="Bermuda", value=89.877655),
        DataItem(label="Bhutan", value=76.543433),
    ]

    return DataCollection(items={item.label: item for item in items})


@pytest.fixture
def data_results():
    return DataResult(
        indicator="Total Energy Consumption per capita",
        year=None,
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
