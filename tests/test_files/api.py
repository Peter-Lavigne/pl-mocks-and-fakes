from dataclasses import dataclass

from pl_mocks_and_fakes.mocks import (
    THIRD_PARTY_API_MOCK_REASONS,
    MockInUnitTests,
)


@dataclass
class Item:
    id: int
    name: str


@MockInUnitTests(*THIRD_PARTY_API_MOCK_REASONS)
def create_item(_name: str) -> Item:
    msg = "This function should be mocked in tests"
    raise NotImplementedError(msg)


@MockInUnitTests(*THIRD_PARTY_API_MOCK_REASONS)
def fetch_item(_id: int) -> Item:
    msg = "This function should be mocked in tests"
    raise NotImplementedError(msg)
