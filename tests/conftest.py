from pl_mocks_and_fakes import initialize_mocks
from pl_mocks_and_fakes.fakes import create_fakes

from . import test_files


def pytest_runtest_setup() -> None:
    initialize_mocks(test_files)
    create_fakes(test_files)
