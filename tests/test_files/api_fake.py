from pl_mocks_and_fakes.fakes import Fake, fake
from pl_mocks_and_fakes.mocks import mock_for
from tests.test_files.api import Item, create_item, fetch_item


@fake()
class ApiFake(Fake):
    def __init__(self) -> None:
        def _create_item_side_effect(_name: str) -> Item:
            item = Item(id=len(self.items) + 1, name=_name)
            self.items.append(item)
            return item

        def _fetch_item_side_effect(_id: int) -> Item:
            for item in self.items:
                if item.id == _id:
                    return item
            msg = f"Item with id {_id} not found"
            raise ValueError(msg)

        self.items: list[Item] = []

        mock_for(create_item).side_effect = _create_item_side_effect
        mock_for(fetch_item).side_effect = _fetch_item_side_effect

    def create_item(self, name: str) -> Item:
        return mock_for(create_item)(name)

    def fetch_item(self, _id: int) -> Item:
        return mock_for(fetch_item)(_id)
