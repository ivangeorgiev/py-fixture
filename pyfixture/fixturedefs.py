import dataclasses
from collections.abc import Callable

from .exceptions import FixtureDoesNotExist


@dataclasses.dataclass(frozen=True)
class FixtureDef:
    name: str
    func: Callable

    def as_dict(self):
        return {
            "name": self.name,
            "func": self.func,
        }


class FixtureDefs:
    _defs: dict

    def __init__(self):
        self._defs = {}

    def put(self, fixture: FixtureDef):
        self._defs[fixture.name] = fixture

    def get(self, name) -> FixtureDef:
        if self.exists(name):
            return self._defs[name]
        msg = f"Fixture with name `{name}` does not exist. Available fixtures: {','.join(self._defs.keys())}"
        raise FixtureDoesNotExist(msg)

    def exists(self, name):
        return name in self._defs


default_registry = FixtureDefs()
