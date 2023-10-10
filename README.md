# py-fixture

[![Documentation Status](https://readthedocs.org/projects/py-fixture/badge/?version=latest)](https://py-fixture.readthedocs.io/en/latest/?badge=latest)

`pytest` style fixtures

Features:

* `fixture` decorator to mark function as fixture factory
* *Fixture Scope* - unit of work for fixture value evaluation
* *Fixture Context* - Fixture Scope is also a context manager
* *Value Cache* - Fixture value is evaluated only once per scope
* *Fixture Factory Argument Replacement* - Invoke fixture factory with replaced arguments
* *Generator Fixture* - Generator function could be used as fixture factory
* *Scope tear down* - through `.finish()` method. Individual fixtures are torn down in reverse order of their evaluation
* *Generator fixture tear down*

## Examples

### Basic Example

This basic example demonstrates the `fixture` decorator, fixture scope and value cache.

```python
from pyfixture import fixture, FixtureScope
@fixture
def x():
    print("Evaluate x")
    return 1

scope = FixtureScope()
scope.get_fixture_value('x')
# Evaluate x
# 1
scope.get_fixture_value('x')
# 1
```

### Advanced Example

This example build on the basic example by demostrating additional features:

* Fixture factory argument replacement
* Fixture Context - fixture scope using context manager
* Generator fixture
* Scope tear down
* Generator fixture tear down

```python
from pyfixture import fixture, FixtureScope

@fixture
def x():
    print("Evaluate x")
    yield 1
    print("Tear down x")

@fixture
def y():
    print("Evaluate y")
    yield 2
    print("Tear down y")

@fixture
def z(x, y):
    print("Evaluate z")
    yield x + y
    print("Tear down z")

def i_am_not_fixture(a, x, y, z):
    print(f"i_am_not_function: a: {a}, x: {x}, y:{y}, z:{z}")

with FixtureScope() as scope:
    print("Get z for the first time")
    assert scope.get_fixture_value("z") == 3
    print("Get z for the second time")
    assert scope.get_fixture_value("z") == 3
    print("Bind a function")
    binded = scope.bind(i_am_not_fixture)
    binded(200)
    print("Finish scope")
# Get z for the first time
# Evaluate x
# Evaluate y
# Evaluate z
# Get z for the second time
# Bind a function
# i_am_not_function: a:200, x: 1, y:2, z:3
# Finish scope
# Tear down z
# Tear down y
# Tear down x
```

### Reallistic Example

```python
from pyfixture import fixture, FixtureScope

@fixture
def existing_user():
    user = User.objects.get_or_create(username="myuser")
    yield user
    user.delete()

@fixture(name="given_existing_order")
def existing_order(existing_user):
    order = Order.objects.get_or_create(id=1, user=existing_user)
    yield order
    order.delete()

scope = FixtureScope()
order = scope.get_fixture_value("existing_order")
user = scope.get_fixture_value("user")
assert order.user is user
# ...

```
