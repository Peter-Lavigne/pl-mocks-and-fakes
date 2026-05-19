from tests.test_files.nested_test_files_1.nested_test_files_2.deeply_nested_function_to_mock import (
    deeply_nested_function_to_mock,
)


def function_that_calls_function_to_mock() -> int:
    return deeply_nested_function_to_mock() + 10
