from collections.abc import Callable
from typing import Any, cast, get_type_hints
from unittest.mock import Mock

from pl_mocks_and_fakes.default_value import default_value


def default_mock_return_value[T](func: Callable[..., T]) -> T:
    """
    Return a Mock configured as a default for the given callable.

    For regular functions, the mock's return_value is the default for the
    function's return type. For context managers (e.g. @contextmanager),
    the mock returns an object that supports __enter__/__exit__ and
    __enter__ returns the default for the return type.
    """

    def _is_context_manager(func: Any) -> bool:  # noqa: ANN401
        # A return type of "Generator" is insufficient to determine that the function is a context manager.
        return (
            hasattr(func, "__code__")
            and "_GeneratorContextManager" in func.__code__.co_names
        )

    return_type = get_type_hints(func)["return"]
    return_value = cast("Any", default_value(return_type))
    if _is_context_manager(func):
        ctm_return_value = Mock()
        ctm_return_value.__enter__ = Mock()
        ctm_return_value.__enter__.return_value = return_value
        ctm_return_value.__exit__ = Mock()
        return ctm_return_value
    return return_value
