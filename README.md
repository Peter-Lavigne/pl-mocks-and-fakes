# pl-mocks-and-fakes

Mock slow, nondeterministic, and side-effect-producing code with minimal per-test configuration.

## Project Status

Alpha. Expect breaking changes.

## Installation

```
uv add pl-mocks-and-fakes
```

## Usage (Mocks)

```python
# your_package/your_module.py

from pl_mocks_and_fakes import MockInUnitTests, MockReason
import random

@MockInUnitTests(MockReason.NONDETERMINISTIC)
def random_int() -> int:
    return random.randint(0, 100)

@MockInUnitTests(MockReason.NONDETERMINISTIC)
def random_string() -> str:
    return random.choice(["foo", "bar", "baz"])

def random_int_and_string() -> tuple[int, str]:
    return random_int(), random_string()



# your_test_package/conftest.py

import pytest
from pl_mocks_and_fakes import initialize_mocks
import your_package

def pytest_runtest_setup(item: pytest.Item) -> None:
    initialize_mocks(your_package)



# your_test_package/your_module_test.py

from pl_mocks_and_fakes import stub, mock_for
from your_package.your_module import random_int, random_int_and_string, random_string

def test_random_int_and_string() -> None:
    stub(random_int)(5) # Use `stub` to set the return value of a mock for a specific test.
    mock_for(random_string).return_value = "foo" # Use `mock_for` to get the Mock object.

    result = random_int_and_string()

    assert result == (5, "foo")
```

## Usage (Fakes)

```python
# your_package/your_module.py

from dataclasses import dataclass

from pl_mocks_and_fakes import Fake, MockInUnitTests, THIRD_PARTY_API_MOCK_REASONS

@dataclass
class JiraTicket:
    id: str
    title: str


@MockInUnitTests(*THIRD_PARTY_API_MOCK_REASONS)
def create_jira_ticket(title: str) -> str:
    # This makes a third-party API call.
    # ...
    pass

@MockInUnitTests(*THIRD_PARTY_API_MOCK_REASONS)
def fetch_jira_ticket(ticket_id: str) -> JiraTicket:
    # This makes a third-party API call.
    # ...
    pass

def duplicate_jira_ticket(ticket_id: str) -> str:
    ticket = fetch_jira_ticket(ticket_id)
    return create_jira_ticket(title=ticket.title)



# your_test_package/conftest.py

import pytest
from pl_mocks_and_fakes import create_fakes
import your_test_package

def pytest_runtest_setup(item: pytest.Item) -> None:
    create_fakes(your_test_package)



# your_test_package/jira_fake.py

from pl_mocks_and_fakes import Fake, mock_for
from your_package.your_module import JiraTicket, create_jira_ticket, fetch_jira_ticket

class JiraFake(Fake):
    def __init__(self):
        def _create_jira_ticket_side_effect(title: str) -> str:
            ticket_id = f"FAKE-{len(self.tickets) + 1}"
            self.tickets.append(JiraTicket(id=ticket_id, title=title))
            return ticket_id

        def _fetch_jira_ticket_side_effect(ticket_id: str) -> JiraTicket:
            for ticket in self.tickets:
                if ticket.id == ticket_id:
                    return ticket
            raise ValueError(f"Ticket with id {ticket_id} not found")

        self.tickets: list[JiraTicket] = []
        mock_for(create_jira_ticket).side_effect = _create_jira_ticket_side_effect
        mock_for(fetch_jira_ticket).side_effect = _fetch_jira_ticket_side_effect



# your_test_package/your_module_test.py

from pl_mocks_and_fakes import fake_for
from your_package.your_module import duplicate_jira_ticket, create_jira_ticket, fetch_jira_ticket
from your_test_package.jira_fake import JiraFake

def test_duplicate_jira_ticket() -> None:
    # Use functions with Fake implementations as if they were the real functions. The Fake will be used instead.
    ticket_id = create_jira_ticket("Ticket Name")

    duplicated_ticket_id = duplicate_jira_ticket(ticket_id)

    assert ticket_id != duplicated_ticket_id
    assert fetch_jira_ticket(duplicated_ticket_id).title == "Ticket Name"
    # Use `fake_for` to get the Fake object.
    assert len(fake_for(JiraFake).tickets) == 2
```

## Releasing

Run `./release.sh`.

## License

Licensed under the Apache License 2.0. See [LICENSE](./LICENSE).
