from pl_mocks_and_fakes.mocks import MockInUnitTests, MockReason


@MockInUnitTests(MockReason.UNMITIGATED_SIDE_EFFECT)
def deeply_nested_function_to_mock() -> int:
    msg = "This function should be mocked in unit tests"
    raise NotImplementedError(msg)
