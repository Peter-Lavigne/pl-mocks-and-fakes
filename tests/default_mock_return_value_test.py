from collections.abc import Generator
from contextlib import contextmanager

from pl_mocks_and_fakes.default_mock_return_value import default_mock_return_value


def test_default_mock_return_value() -> None:
    def _int_returning_function() -> int:
        return 30  # Arbitrary non-default value

    return_value = default_mock_return_value(_int_returning_function)
    assert return_value == 0


def test_default_mock_return_value_for_context_manager() -> None:
    @contextmanager
    def _int_yielding_context_manager() -> Generator[int]:
        yield 30  # Arbitrary non-default value

    return_value = default_mock_return_value(_int_yielding_context_manager)

    with return_value as value:
        assert value == 0
