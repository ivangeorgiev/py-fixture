from collections import OrderedDict
import inspect
from typing import Any, Generator
from .fixturedefs import FixtureDef, FixtureDefs, default_registry


class FixtureClosure:
    value: Any

    def __init__(self, value):
        self.value = value

    def finish(self):
        pass # pragma: no cover


class GeneratorFixtureClosure(FixtureClosure):
    gen: Generator

    def __init__(self, gen):
        self.gen = gen
        self.value = next(gen)

    def finish(self):
        try:
            next(self.gen)
        except StopIteration:
            pass


class FixtureScope:
    _registry: FixtureDefs
    _value_cache: OrderedDict[str, FixtureClosure]

    def __init__(self, registry: FixtureDefs = None):
        self._registry = registry or default_registry
        self._value_cache = OrderedDict()

    def get_fixture_value(self, name):
        self._ensure_in_cache(name)
        return self._value_cache[name].value

    def finish(self):
        for name in reversed(self._value_cache.keys()):
            self._value_cache[name].finish()
        self._value_cache.clear()

    def _ensure_in_cache(self, fixture_name):
        if fixture_name in self._value_cache:
            return
        fixture_def = self._registry.get(fixture_name)
        closure = self._evaluate_fixture(fixture_def)
        self._value_cache[fixture_name] = closure

    def _evaluate_fixture(self, fixture_def: FixtureDef):
        func = fixture_def.func
        value = self._invoke_function(func)
        closure_class = self._get_closure_class(func)
        return closure_class(value)

    def _invoke_function(self, func):
        signature = inspect.signature(func)
        args = {param_name: self.get_fixture_value(param_name) for param_name in signature.parameters}
        return func(**args)

    def _get_closure_class(self, func):
        if inspect.isgeneratorfunction(func):
            return GeneratorFixtureClosure
        return FixtureClosure
