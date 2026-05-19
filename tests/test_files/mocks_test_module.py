from tests.test_files.module_to_mock import function_to_mock
from tests.test_files.nested_test_files_1.function_that_calls_function_to_mock import (
    function_that_calls_function_to_mock,
)


def function_being_tested() -> int:
    return 2 * function_to_mock()


def function_that_calls_function_that_calls_function_to_mock() -> int:
    return function_that_calls_function_to_mock() + 100
