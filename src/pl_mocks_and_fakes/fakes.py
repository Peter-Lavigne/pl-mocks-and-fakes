import importlib
import pkgutil
from functools import cache
from types import ModuleType
from typing import cast


class Fake:
    # Inherit from this class to create a fake. The fake will be automatically created and returned by `fake_for` when requested.
    pass


_fakes: dict[type[Fake], Fake] = {}


@cache
def _fake_classes(package_path: str, package_name: str) -> list[type[Fake]]:
    result: list[type[Fake]] = []
    for module_info in pkgutil.iter_modules([package_path]):
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        for attr_name in dir(module):
            cls = getattr(module, attr_name)
            if isinstance(cls, type) and issubclass(cls, Fake) and cls is not Fake:
                result.append(cls)
    return result


def fake_for[T: Fake](fake_type: type[T]) -> T:
    assert fake_type in _fakes, f"No fake found for type: {fake_type}"
    return cast("T", _fakes[fake_type])


def create_fakes(*packages: ModuleType) -> None:
    global _fakes  # noqa: PLW0603
    _fakes = {}
    for package in packages:
        assert len(package.__path__) == 1, "Expected package to have exactly one path"
        package_path = package.__path__[0]
        package_name = package.__name__
        for fake_class in _fake_classes(package_path, package_name):
            _fakes[fake_class] = fake_class()
