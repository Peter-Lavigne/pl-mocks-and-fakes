from typing import cast


class Fake:
    pass


_fakes: dict[type[Fake], Fake] = {}


def fake_for[T: Fake](fake_type: type[T]) -> T:
    assert fake_type in _fakes, f"No fake found for type: {fake_type}"
    return cast("T", _fakes[fake_type])


def create_fakes(*fakes: type[Fake]) -> None:
    for fake in fakes:
        _fakes[fake] = fake()
