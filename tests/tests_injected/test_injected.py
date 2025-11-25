"""
The tests here are test designed to fail with their current
parameters and fixtures. To make them pass, the outer plugin
tests should inject appropriate parameters, that will make them pass,
and by that validate that the injection mechanism is working.
"""
import pytest
from argument_values import INJECTED, NOT_EFFECTED


@pytest.fixture(scope="module")
def injected_string_fixture() -> str:
    return NOT_EFFECTED


@pytest.fixture(scope="module")
def other_indirect_arg() -> str:
    return NOT_EFFECTED


@pytest.mark.parametrize(
    "injected_string_parameter",
    [
        NOT_EFFECTED,
    ]
)
def test_inject_1_string_parameterize(
        injected_string_parameter: str,
):
    """
    Inject "injected_string_parameter"="injected" to make this test pass.
    """
    assert injected_string_parameter == INJECTED


def test_inject_1_string_fixture(
        injected_string_fixture: str,
):
    """
    Inject "injected_string_fixture"="injected" to make this test pass.
    """
    assert injected_string_fixture == INJECTED


@pytest.mark.parametrize(
    "injected_indirect_arg,other_indirect_arg",
    [
        (NOT_EFFECTED, NOT_EFFECTED),
    ],
    indirect=True
)
def test_inject_and_override_indirect_for_indirect_true_while_not_effecting_other_indirect_arguments(
        injected_indirect_arg: str,
        other_indirect_arg: str,
):
    """
    Inject "injected_string_fixture"="injected" to make this test pass, while not effecting
    other_indirect_arg, which needs to stay indirect to pass.
    Check that when injecting on indirect=True, none injected indirect arguments are not effected.
    """
    assert injected_indirect_arg == INJECTED
    assert other_indirect_arg == NOT_EFFECTED


@pytest.mark.parametrize(
    "injected_indirect_arg,other_indirect_arg",
    [
        (NOT_EFFECTED, NOT_EFFECTED),
    ],
    indirect=["injected_indirect_arg", "other_indirect_arg"]
)
def test_inject_and_override_indirect_for_indirect_equal_list_with_all_test_arguments(
        injected_indirect_arg: str,
        other_indirect_arg: str,
):
    """
    Inject "injected_string_fixture"="injected" to make this test pass, while not effecting
    other_indirect_arg, which needs to stay indirect to pass.
    Check that when injecting on indirect=["injected_indirect_arg", "other_indirect_arg"],
    none injected indirect arguments are not effected.
    """
    assert injected_indirect_arg == INJECTED
    assert other_indirect_arg == NOT_EFFECTED


@pytest.mark.parametrize(
    "a,b,c",
    [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9)
    ]
)
def test_general_duplication_deletion(a, b, c):
    """
    Injection target for tests checking parameterize arguments set
    duplication deletion.
    """


@pytest.mark.parametrize(
    "a,b,c",
    [
        (1, 2, 3),
        (1, 2, 3),
        (1, 2, 3)
    ]
)
def test_parameter_set_duplication_preservation(a, b, c):
    """
    Injection target for tests checking original parameterize arguments set
    duplication preservation.
    """
