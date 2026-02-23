from tests.test_files.module_to_mock import function_to_mock


def function_being_tested() -> int:
    return 2 * function_to_mock()
