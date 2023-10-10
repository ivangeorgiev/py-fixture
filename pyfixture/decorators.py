import dataclasses
import inspect
from typing import Callable
from .fixturedefs import FixtureDef, default_registry

@dataclasses.dataclass(frozen=True)
class FixtureFunctionDecorator:
    name: str
    
    def __call__(self, func: Callable):
        if inspect.isclass(func):
            raise ValueError("class fixtures are not supported")

        name = self.name or func.__name__
        definition = FixtureDef(name, func)
        default_registry.put(definition)
        return func

def fixture(func=None, *, name=None):
    """
    Decortor that registers function as fixture source
    """
    fixture_decorator = FixtureFunctionDecorator(name)

    # Direct decorator
    if func:
        return fixture_decorator(func)
    return fixture_decorator
