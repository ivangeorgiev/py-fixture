from unittest.mock import Mock

import pytest
from pyfixture.decorators import fixture
from pyfixture.fixturedefs import default_registry, FixtureDef


def assert_fixture_def(expected: FixtureDef, actual: dict):
    __tracebackhide__ = True
    if isinstance(expected, FixtureDef):
        expected = expected.as_dict()
    if isinstance(actual, FixtureDef):
        actual = actual.as_dict()
    assert expected == actual


class TestFixtureDecorator:
    def test_should_register_function_direct_decorator(self):
        func = Mock()
        func.__name__ = "decorated_fixture"
        result = fixture(func)
        assert result == func
        assert default_registry.exists("decorated_fixture")
        fixture_def = default_registry.get("decorated_fixture")
        assert isinstance(fixture_def, FixtureDef)
        assert_fixture_def({"name": "decorated_fixture", "func": func}, fixture_def)

    def test_should_register_function_argument_decorator(self):
        func = Mock()
        func.__name__ = "decorated_fixture"
        result = fixture(name="decorator_name")(func)
        assert result == func
        assert default_registry.exists("decorator_name")
        fixture_def = default_registry.get("decorator_name")
        assert isinstance(fixture_def, FixtureDef)
        assert_fixture_def({"name": "decorator_name", "func": func}, fixture_def)

    def test_class_fixtures_not_supported(self):
        class FakeFixture:
            pass

        with pytest.raises(ValueError, match="class fixtures are not supported"):
            fixture(name="decorator_name")(FakeFixture)
