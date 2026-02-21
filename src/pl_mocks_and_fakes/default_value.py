from collections.abc import Callable, Generator
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from functools import cache
from inspect import isclass
from pathlib import Path
from types import NoneType, UnionType
from typing import (
    Any,
    Literal,
    NamedTuple,
    TypeAliasType,
    TypeGuard,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
    overload,
)

from pydantic import BaseModel


@overload
def default_value(return_type: type[str]) -> str: ...
@overload
def default_value(return_type: type[bool]) -> bool: ...
@overload
def default_value(return_type: type[int]) -> int: ...
@overload
def default_value(return_type: type[float]) -> float: ...
@overload
def default_value(return_type: NoneType) -> NoneType: ...
@overload
def default_value(return_type: type[timedelta]) -> timedelta: ...
@overload
def default_value(return_type: type[datetime]) -> datetime: ...
@overload
def default_value(return_type: type[date]) -> date: ...
@overload
def default_value(return_type: type[Path]) -> Path: ...
@overload
def default_value[T](return_type: type[list[T]]) -> list[T]: ...
@overload
def default_value[T, U](return_type: type[dict[T, U]]) -> dict[T, U]: ...
@overload
def default_value(return_type: type[tuple[Any, ...]]) -> tuple[Any, ...]: ...
@overload
def default_value(return_type: object) -> Any:  # noqa: ANN401
    # Fallback for complex types. I tried to make UnionType work to no avail, after which I didn't try to fix many of the others.
    ...


def _is_namedtuple(obj: object) -> TypeGuard[NamedTuple]:
    # Source: https://stackoverflow.com/a/2166841
    return hasattr(obj, "_fields") and isclass(obj) and issubclass(obj, tuple)


def _is_type_from_module(obj: object, module: str, name: str) -> bool:
    return (
        getattr(obj, "__module__", None) == module
        and getattr(obj, "__name__", None) == name
    )


@cache
def default_value(return_type: object) -> Any:  # noqa: ANN401
    if return_type is str:
        return ""
    if return_type is int:
        return 0
    if return_type is bool:
        return False
    if return_type is float:
        return 0.0
    if return_type is NoneType:
        return None
    if return_type is timedelta:
        return timedelta(0)
    if return_type is datetime or _is_type_from_module(
        return_type, "datetime", "datetime"
    ):
        return datetime.min
    if return_type is date or _is_type_from_module(return_type, "datetime", "date"):
        return date.min
    if return_type is Path or _is_type_from_module(return_type, "pathlib", "Path"):
        return Path()
    if isinstance(return_type, TypeAliasType):
        return default_value(return_type.__value__)  # type: ignore[return-value]
    if isinstance(return_type, TypeVar):
        return None
    if get_origin(return_type) is list:
        return []
    if get_origin(return_type) is dict:
        return {}
    if get_origin(return_type) is tuple:
        subtypes = get_args(return_type)
        return tuple(default_value(t) for t in subtypes)  # type: ignore[return-value]
    if get_origin(return_type) is Callable:

        def function(*_args: list[Any], **_kwargs: dict[str, Any]) -> Any:  # noqa: ANN401
            function_return_type = get_args(return_type)[-1]
            return default_value(function_return_type)  # type: ignore[return-value]

        return function
    if isinstance(return_type, UnionType):
        first_argument = get_args(return_type)[0]
        return default_value(first_argument)  # type: ignore[return-value]
    if get_origin(return_type) is Literal:
        args = get_args(return_type)
        if args:
            return args[0]
    if is_typeddict(return_type):
        type_hints = get_type_hints(return_type)
        default_dict: dict[str, Any] = {}
        for key, key_type in type_hints.items():
            default_dict[key] = default_value(key_type)
        return default_dict
    if _is_namedtuple(return_type):
        type_hints = get_type_hints(return_type)
        field_types = [type_hints[field] for field in return_type._fields]
        return return_type(*[default_value(t) for t in field_types])  # type: ignore[return-value]
    if get_origin(return_type) is Generator:

        def generator_function() -> Generator[None]:
            return
            yield  # Needed to make this a generator

        return generator_function
    if isclass(return_type) and issubclass(return_type, BaseModel):
        field_values: dict[str, Any] = {}
        for field_name, field_info in return_type.model_fields.items():
            field_values[field_name] = default_value(field_info.annotation)
        return return_type(**field_values)
    if is_dataclass(return_type):
        field_values = {
            f.name: default_value(f.type)  # type: ignore[return-value]
            for f in fields(return_type)
        }
        return return_type(**field_values)  # type: ignore[return-value]
    msg = f"No default value set for {return_type}"
    raise NotImplementedError(msg)
