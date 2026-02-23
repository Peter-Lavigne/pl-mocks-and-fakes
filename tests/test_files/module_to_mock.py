from pl_mocks_and_fakes.mocks import MockInUnitTests, MockReason


@MockInUnitTests(MockReason.UNMITIGATED_SIDE_EFFECT)
def function_to_mock() -> int:
    msg = "This function should be mocked in tests"
    raise NotImplementedError(msg)
