import importlib
import pkgutil
from collections.abc import Callable
from types import ModuleType
from typing import cast


class Fake:
    # Inherit from this class to create a fake. The fake will be automatically created and returned by `fake_for` when requested.
    pass


_fake_classes: set[type[Fake]] = set()
_fakes: dict[type[Fake], Fake] = {}


def fake[T: Fake]() -> Callable[[type[T]], type[T]]:
    # Decorator to mark a class as a fake. The fake will be automatically created and returned by `fake_for` when requested.
    def decorator(cls: type[T]) -> type[T]:
        _fake_classes.add(cls)
        return cls

    return decorator


def fake_for[T: Fake](fake_type: type[T]) -> T:
    assert fake_type in _fakes, f"No fake found for type: {fake_type}"
    return cast("T", _fakes[fake_type])


_fakes_initialized = False
_using_fakes = False


def create_fakes(package: ModuleType) -> None:
    global _fakes_initialized  # noqa: PLW0603
    global _using_fakes  # noqa: PLW0603
    _using_fakes = True

    if not _fakes_initialized:
        assert len(package.__path__) == 1, "Expected package to have exactly one path"
        package_path = package.__path__[0]
        package_name = package.__name__

        for module_info in pkgutil.iter_modules([package_path]):
            importlib.import_module(f"{package_name}.{module_info.name}")

        for cls in _fake_classes:
            _fakes[cls] = cls()

        _fakes_initialized = True
    else:
        for fake_instance in _fakes.values():
            fake_instance.__init__()
