import pytest
from pyfixture.exceptions import FixtureDoesNotExist
from pyfixture.fixturedefs import FixtureDef, FixtureDefs


class TestFixtureDefsClass:
    def test_can_register_fixture(self, defs: FixtureDefs):
        fixture = FixtureDef("my_fixture", lambda: 1)
        defs.put(fixture)
        assert defs.exists("my_fixture")

    def test_can_retrieve_fixture(self, defs: FixtureDefs, registered_fixture: FixtureDef):
        fixture = defs.get("my_fixture")
        assert fixture is registered_fixture

    def test_should_raise_fixturedoesnotexist_if_fixture_is_not_registered(self, defs: FixtureDefs):
        with pytest.raises(FixtureDoesNotExist):
            defs.get("who_am_i")


@pytest.fixture(name="defs")
def given_defs() -> FixtureDefs:
    return FixtureDefs()


@pytest.fixture(name="registered_fixture")
def given_registered_fixture(defs: FixtureDef) -> FixtureDef:
    fixture = FixtureDef("my_fixture", lambda: 1)
    defs.put(fixture)
    return fixture
