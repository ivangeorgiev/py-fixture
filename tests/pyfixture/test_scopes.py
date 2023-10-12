from unittest.mock import Mock, patch

import pytest

from pyfixture.exceptions import FixtureDoesNotExist, RecursiveFixtureEvaluation
from pyfixture.fixturedefs import FixtureDef, FixtureDefs, default_registry
from pyfixture.scopes import FixtureClosure, FixtureScope


class TestFixtureScopeClass:
    def test_should_use_global_registry_if_not_specified(self):
        sess = FixtureScope()
        assert sess._registry is default_registry

    @pytest.mark.usefixtures("registered_fixture")
    def test_evaluates_fixture_value(self, fixture_scope: FixtureScope):
        value = fixture_scope.get_fixture_value("fixture")
        assert value == "fixture value"

    @pytest.mark.usefixtures("registered_fixture")
    @patch.object(FixtureScope, "_evaluate_fixture")
    def test_value_is_evaluated_only_once(self, mock_evaluate: Mock, fixture_scope):
        fixture_scope.get_fixture_value("fixture")
        fixture_scope.get_fixture_value("fixture")
        mock_evaluate.assert_called_once()

    @pytest.mark.usefixtures("registered_fixture")
    @pytest.mark.usefixtures("registered_fixture_with_args")
    def test_evaluates_fixture_with_args(self, fixture_scope: FixtureScope):
        value = fixture_scope.get_fixture_value("fixture_with_args")
        assert value == "fixture value with args"

    @pytest.mark.usefixtures("registered_generator_fixture")
    def test_evaluates_generator_fixtures(self, fixture_scope: FixtureScope):
        value = fixture_scope.get_fixture_value("generator_fixture")
        assert value == "fixture from generator"

    @pytest.mark.usefixtures("registered_fixture")
    @patch.object(FixtureClosure, "finish")
    def test_finish_should_finish_evaluated_fixtures(self, mock_finish: Mock, fixture_scope: FixtureScope):
        fixture_scope.get_fixture_value("fixture")
        fixture_scope.finish()
        mock_finish.assert_called_once()

    def test_finish_should_tear_down_evaluated_generator_fixtures(
        self, fixture_scope: FixtureScope, registered_generator_fixture
    ):
        fixture_scope.get_fixture_value("generator_fixture")
        fixture_scope.finish()
        assert registered_generator_fixture._tests_fixture_torn_down

    @patch.object(FixtureScope, "finish")
    def test_scope_as_context_manager(self, mock_finish, registry):
        with FixtureScope(registry) as context:
            assert isinstance(context, FixtureScope)
        mock_finish.assert_called_once()

    @pytest.mark.usefixtures("registered_fixture")
    def test_bind_should_raise_exeception_arguments_do_not_match_fixture(self, fixture_scope: FixtureScope):
        def some_function(some_argument, fixture):
            return f"got `{fixture}` and `{some_argument}`"

        with pytest.raises(FixtureDoesNotExist):
            fixture_scope.bind(some_function)

    @pytest.mark.usefixtures("registered_fixture")
    def test_bind_should_bind_arguments_to_known_fixtures_by_name_with_ignore_missing(
        self, fixture_scope: FixtureScope
    ):
        def some_function(some_argument, fixture):
            return f"got `{fixture}` and `{some_argument}`"

        bound = fixture_scope.bind(some_function, ignore_missing=True)
        result = bound("passed argument")
        assert result == "got `fixture value` and `passed argument`"

    def test_detect_recursive_fixture_evaluation(self, fixture_scope: FixtureScope):
        def one(two):
            return two

        def two(one):
            return one

        registry = fixture_scope._registry
        registry.put(FixtureDef("one", one))
        registry.put(FixtureDef("two", two))

        with pytest.raises(
            RecursiveFixtureEvaluation,
            match="Recursive fixture evaluation detected for fixture `one`. Evaluation order: one, two, one",
        ):
            fixture_scope.get_fixture_value("one")


@pytest.fixture(name="registry")
def given_registry():
    return FixtureDefs()


@pytest.fixture(name="fixture_scope")
def given_fixture_scope(registry):
    yield FixtureScope(registry)


@pytest.fixture(name="fixture_context")
def given_fixture_context(registry):
    with FixtureScope(registry) as scope:
        yield scope


@pytest.fixture(name="registered_fixture")
def given_registered_fixture(registry: FixtureDefs):
    def fake_fixture():
        return "fixture value"

    fixture_def = FixtureDef("fixture", fake_fixture)
    registry.put(fixture_def)
    return fake_fixture


@pytest.fixture(name="registered_fixture_with_args")
def given_registered_fixture_with_args(registry: FixtureDefs):
    def fake_fixture_with_args(fixture):
        return f"{fixture} with args"

    fixture_def = FixtureDef("fixture_with_args", fake_fixture_with_args)
    registry.put(fixture_def)
    return fake_fixture_with_args


@pytest.fixture(name="registered_generator_fixture")
def given_registered_generator_fixture(registry: FixtureDefs):
    def fake_generator_fixture():
        yield "fixture from generator"
        fake_generator_fixture._tests_fixture_torn_down = True

    fixture_def = FixtureDef("generator_fixture", fake_generator_fixture)
    registry.put(fixture_def)
    return fake_generator_fixture
