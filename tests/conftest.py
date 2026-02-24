from pl_mocks_and_fakes import initialize_mocks
from pl_mocks_and_fakes.fakes import create_fakes
from tests.test_files.api_fake import ApiFake


def pytest_runtest_setup() -> None:
    initialize_mocks()
    create_fakes(ApiFake)
