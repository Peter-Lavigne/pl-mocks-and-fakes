import functools
import importlib
import pkgutil
from collections.abc import Callable
from enum import Enum
from types import ModuleType
from typing import Any, ParamSpec, TypeVar
from unittest.mock import Mock

from pl_mocks_and_fakes.default_mock_return_value import default_mock_return_value


class MockReason(Enum):
    # The code is too slow to run frequently
    SLOW = "slow"
    # The code is nondeterministic, so tests using it would themselves be nondeterministic.
    NONDETERMINISTIC = "nondeterministic"
    # The code has an unmitigated side effect that makes frequent calls undesirable, such as making third-party API calls or modifying files in this repo.
    UNMITIGATED_SIDE_EFFECT = "unmitigated_side_effect"
    # (Legacy/Deprecated) I have not yet investigated why we mock this code. Consider investigating and assigning a more specific reason.
    UNINVESTIGATED = "uninvestigated"


HUMAN_INTERACTION_MOCK_REASONS = {
    MockReason.SLOW,
    MockReason.NONDETERMINISTIC,
    MockReason.UNMITIGATED_SIDE_EFFECT,
}

THIRD_PARTY_API_MOCK_REASONS = {
    MockReason.SLOW,
    MockReason.NONDETERMINISTIC,
    MockReason.UNMITIGATED_SIDE_EFFECT,
}

P = ParamSpec("P")
R = TypeVar("R")

_mocked_functions: set[Callable[..., Any]] = set()


def MockInUnitTests(*_: MockReason) -> Callable[[Callable[P, R]], Callable[P, R]]:  # noqa: N802
    # MockReason is set solely for documentation purposes

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if _using_mocks and wrapper in _mocks:
                return _mocks[wrapper](*args, **kwargs)
            return func(*args, **kwargs)  # pragma: no cover

        _mocked_functions.add(wrapper)
        return wrapper

    return decorator


# Global variable holding all mocks
_mocks: dict[Callable[..., Any], Mock] = {}
_mocks_initialized = False
_using_mocks = False


def initialize_mocks(package: ModuleType) -> None:
    global _mocks_initialized  # noqa: PLW0603
    global _using_mocks  # noqa: PLW0603
    _using_mocks = True

    # assert len(package.__path__) == 1, "Expected package to have exactly one path"
    package_path = package.__path__[0]
    package_name = package.__name__

    if not _mocks_initialized:
        for module_info in pkgutil.iter_modules([package_path]):
            # Import all modules in src to populate the registry of functions to mock.
            importlib.import_module(f"{package_name}.{module_info.name}")

        for func in _mocked_functions:
            _mocks[func] = Mock(name=f"Mock for {func.__module__}.{func.__qualname__}")
            _mocks[func].return_value = default_mock_return_value(
                func.__wrapped__  # type: ignore[attr-defined]
            )

        _mocks_initialized = True
    else:
        for func, mock in _mocks.items():
            mock.reset_mock(return_value=True, side_effect=True)
            mock.return_value = default_mock_return_value(func.__wrapped__)  # type: ignore[attr-defined]


def mock_for(component: Callable[..., Any]) -> Mock:
    assert component in _mocks, (
        f"No mock found for component: {component}"
    )  # pragma: no cover
    return _mocks[component]  # pragma: no cover


def stub[T](component: Callable[..., T]) -> Callable[[T], None]:
    def set_value(value: T) -> None:
        mock = mock_for(component)
        mock.return_value = value

    return set_value
