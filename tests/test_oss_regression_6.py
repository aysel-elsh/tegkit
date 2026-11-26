import pytest

from tegkit import TEGArray, TEGModule


@pytest.fixture
def module():
    return TEGModule(seebeck=0.05, resistance=2.0, thermal_conductance=0.5)


@pytest.mark.parametrize("field", ["series", "parallel"])
@pytest.mark.parametrize("count", [2.5, 0, -1, 2.0, True])
def test_array_rejects_invalid_counts(module, field, count):
    accepted = True
    try:
        TEGArray(module, **{field: count})
    except ValueError:
        accepted = False

    assert not accepted, f"TEGArray accepted {field}={count!r}"


def test_array_accepts_positive_integer_counts(module):
    array = TEGArray(module, series=1, parallel=3)

    assert array.count == 3
