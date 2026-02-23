from tests.test_files.api import Item, create_item, fetch_item


def duplicate_item(item_id: int) -> Item:
    original = fetch_item(item_id)
    return create_item(original.name)
