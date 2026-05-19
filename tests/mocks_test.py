from pl_mocks_and_fakes import mock_for
from pl_mocks_and_fakes.mocks import stub

from .test_files.mocks_test_module import (
    function_being_tested,
    function_that_calls_function_that_calls_function_to_mock,
    function_to_mock,
)


def test_mocks_annotated_functions() -> None:
    function_being_tested()  # Does not raise NotImplementedError because module_to_mock was mocked


def test_mocks_nested_packages() -> None:
    function_that_calls_function_that_calls_function_to_mock()  # Does not raise NotImplementedError because module_to_mock was mocked


def test_stub() -> None:
    stub(function_to_mock)(10)

    assert function_being_tested() == 20


def test_mock_for() -> None:
    mock_for(function_to_mock).return_value = 10

    assert function_being_tested() == 20
