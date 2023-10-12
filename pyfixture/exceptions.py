class PyFixtureException(Exception):
    pass


class FixtureDoesNotExist(PyFixtureException):
    pass


class RecursiveFixtureEvaluation(PyFixtureException):
    pass
