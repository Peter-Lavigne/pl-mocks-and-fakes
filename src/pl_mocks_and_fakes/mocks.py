import importlib
import pkgutil
from collections.abc import Callable
from enum import Enum
from functools import cache
from types import FunctionType, ModuleType
from typing import Any, ParamSpec, TypeVar, cast
from unittest.mock import Mock, patch

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

# Registry of (module_name, func_name) for callables that should be mocked in unit tests.
_MOCKABLE_REGISTRY: set[tuple[str, str]] = set()


class MockInUnitTests:
    def __init__(self, *_: MockReason) -> None:
        # MockReason is set strictly for documentation purposes.
        pass

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        _MOCKABLE_REGISTRY.add((func.__module__, func.__name__))
        return func


@cache
def _functions_to_mock(package_path: str, package_name: str) -> list[FunctionType]:
    result: list[FunctionType] = []
    for module_info in pkgutil.iter_modules([package_path]):
        # Import all modules in src to populate the registry of functions to mock.
        module = importlib.import_module(f"{package_name}.{module_info.name}")
    for module_name, func_name in _MOCKABLE_REGISTRY:
        # Import all modules (including those not in the package) that contain functions to mock, so that we can retrieve the function objects to create mocks for them.
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        result.append(cast("FunctionType", func))
    return result


def _modules_to_patch(
    package_path: str, package_name: str
) -> dict[ModuleType, list[FunctionType]]:
    result: dict[ModuleType, list[FunctionType]] = {}
    all_modules = [
        f"{package_name}.{module_info.name}"
        for module_info in pkgutil.iter_modules([package_path])
    ]
    for m in all_modules:
        if m.endswith(("_test", "_fake")):
            continue  # Skip test and fake modules
        module = importlib.import_module(m)
        module_attributes = dir(module)
        result[module] = [
            f
            for f in _functions_to_mock(package_path, package_name)
            if f.__name__ in module_attributes
        ]
    return result


def _set_up_mocks(package_path: str, package_name: str) -> None:
    for component_function in _functions_to_mock(package_path, package_name):
        mock = Mock()
        mock.return_value = default_mock_return_value(component_function)
        _mocks[component_function] = mock
    for (
        module_to_patch,
        functions_to_mock,
    ) in _modules_to_patch(package_path, package_name).items():
        for f in functions_to_mock:
            patch(
                f"{module_to_patch.__name__}.{f.__name__}",
                new=_mocks[f],
            ).start()


def _reset_mocks(package_path: str, package_name: str) -> None:
    # Reusing mocks instead of creating new ones sped up tests by about 15%.
    for component_function in _functions_to_mock(package_path, package_name):
        _mocks[component_function].reset_mock(return_value=True, side_effect=True)
        _mocks[component_function].return_value = default_mock_return_value(
            component_function
        )


# Global variable holding all mocks
_mocks: dict[FunctionType, Mock] = {}
_mocks_initialized = False


def initialize_mocks(package: ModuleType) -> None:
    global _mocks_initialized  # noqa: PLW0603
    assert len(package.__path__) == 1, "Expected package to have exactly one path"
    package_path = package.__path__[0]
    package_name = package.__name__
    if not _mocks_initialized:
        _set_up_mocks(package_path, package_name)
        _mocks_initialized = True
    else:
        _reset_mocks(package_path, package_name)


def mock_for(component: Callable[..., Any]) -> Mock:
    assert component in _mocks, f"No mock found for component: {component}"
    return _mocks[component]


def stub[T](component: Callable[..., T]) -> Callable[[T], None]:
    def set_value(value: T) -> None:
        mock = mock_for(component)
        mock.return_value = value

    return set_value
