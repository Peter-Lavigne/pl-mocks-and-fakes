from collections.abc import Callable, Generator
from dataclasses import dataclass
from datetime import date, datetime, timedelta, tzinfo
from pathlib import Path
from types import NoneType
from typing import Literal, NamedTuple, TypedDict, TypeVar

import pytest
from pydantic import BaseModel

from pl_mocks_and_fakes.default_value import default_value


def test_returns_zero_for_int() -> None:
    assert default_value(int) == 0


def test_returns_empty_string_for_str() -> None:
    assert default_value(str) == ""


def test_returns_false_for_bool() -> None:
    assert not default_value(bool)


def test_returns_zero_for_float() -> None:
    assert default_value(float) == 0.0


def test_returns_none_for_nonetype() -> None:
    assert default_value(NoneType) is None


def test_returns_zero_time_for_timedelta() -> None:
    assert default_value(timedelta) == timedelta(0)


def test_returns_min_for_datetime() -> None:
    assert default_value(datetime) == datetime.min


def test_returns_min_for_date() -> None:
    assert default_value(date) == date.min


def test_returns_current_dir_for_path() -> None:
    assert default_value(Path) == Path()


def test_returns_first_value_for_literal() -> None:
    assert default_value(Literal["a", "b", "c"]) == "a"
    assert default_value(Literal[1, 2, 3]) == 1


def test_returns_default_dataclass() -> None:
    @dataclass
    class ExampleDataclass:
        field_a: int
        field_b: str

    assert default_value(ExampleDataclass) == ExampleDataclass(0, "")


def test_returns_default_value_of_subtype_for_union() -> None:
    assert default_value(int | str) in (0, "")
    assert default_value(str | int) in (0, "")


def test_returns_empty_list_for_lists() -> None:
    assert default_value(list[int]) == []


def test_returns_empty_dict_for_dicts() -> None:
    assert default_value(dict[str, int]) == {}


def test_returns_default_value_of_subtypes_for_tuples() -> None:
    assert default_value(tuple[int, str]) == (0, "")


def test_returns_default_function() -> None:
    assert default_value(Callable[[int, float], str])(2, 3.0) == ""
    assert not default_value(Callable[[], bool])()


def test_returns_default_named_tuple() -> None:
    class ExampleTuple(NamedTuple):
        field_a: int
        field_b: str

    assert default_value(ExampleTuple) == ExampleTuple(0, "")


def test_returns_default_typeddict() -> None:
    class ExampleTypedDict(TypedDict):
        field_a: int
        field_b: str

    assert default_value(ExampleTypedDict) == ExampleTypedDict(field_a=0, field_b="")


def test_returns_default_generator() -> None:
    generator = default_value(Generator[int])
    assert list(generator()) == []


def test_returns_default_pydantic_model() -> None:
    class ExampleModel(BaseModel):
        field_a: int
        field_b: str

    assert default_value(ExampleModel) == ExampleModel(field_a=0, field_b="")


def test_returns_none_for_type_var() -> None:
    T = TypeVar("T")
    assert default_value(T) is None


type X = int


def test_returns_underlying_type_for_type() -> None:
    assert default_value(X) == 0


def test_raises_not_implemented_error_for_all_other_types() -> None:
    arbitrary_unimplemented_type = tzinfo

    with pytest.raises(
        NotImplementedError,
        match=f"No default value set for {arbitrary_unimplemented_type}",
    ):
        default_value(arbitrary_unimplemented_type)
