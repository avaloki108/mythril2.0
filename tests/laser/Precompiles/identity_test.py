import pytest

from mythril2.laser.ethereum.natives import identity


@pytest.mark.parametrize(
    "input_list, expected_result", (([], []), ([10, 20], [10, 20]))
)
def test_identity(input_list, expected_result):
    assert identity(input_list) == expected_result
