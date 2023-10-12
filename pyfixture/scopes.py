import inspect
from collections import OrderedDict
from collections.abc import Generator
from functools import partial
from typing import Any

from pyfixture.exceptions import RecursiveFixtureEvaluation

from .fixturedefs import FixtureDef, FixtureDefs, default_registry


class FixtureClosure:
    value: Any

    def __init__(self, value):
        self.value = value

    def finish(self):
        pass  # pragma: no cover


class GeneratorFixtureClosure(FixtureClosure):
    gen: Generator

    def __init__(self, gen):
        self.gen = gen
        super().__init__(next(gen))

    def finish(self):
        try:
            next(self.gen)
        except StopIteration:
            pass


class FixtureScope:
    _registry: FixtureDefs
    _value_cache: OrderedDict[str, FixtureClosure]
    _evaluation_stack: list

    def __init__(self, registry: FixtureDefs = None):
        self._registry = registry or default_registry
        self._value_cache = OrderedDict()
        self._evaluation_stack = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.finish()

    def get_fixture_value(self, name):
        if name in self._evaluation_stack:
            msg = f"Recursive fixture evaluation detected for fixture `{name}`. Evaluation order: {', '.join(self._evaluation_stack)}, {name}"
            raise RecursiveFixtureEvaluation(msg)
        self._evaluation_stack.append(name)
        self._ensure_in_cache(name)
        self._evaluation_stack.pop()
        return self._value_cache[name].value

    def finish(self):
        for name in reversed(self._value_cache.keys()):
            self._value_cache[name].finish()
        self._value_cache.clear()

    def bind(self, func, ignore_missing=False):
        signature = inspect.signature(func)
        if ignore_missing:
            args = {
                param_name: self.get_fixture_value(param_name)
                for param_name in signature.parameters
                if self._registry.exists(param_name)
            }
        else:
            args = {param_name: self.get_fixture_value(param_name) for param_name in signature.parameters}
        return partial(func, **args)

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
