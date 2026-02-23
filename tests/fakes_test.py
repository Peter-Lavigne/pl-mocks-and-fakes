from pl_mocks_and_fakes.fakes import fake_for
from tests.test_files.api_fake import ApiFake
from tests.test_files.fakes_test_module import duplicate_item


def test_fakes() -> None:
    item_1 = fake_for(ApiFake).create_item("Test Item")

    item_2 = duplicate_item(item_1.id)

    assert len(fake_for(ApiFake).items) == 2
    assert item_1.name == item_2.name
