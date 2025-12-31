class OptiStackException(Exception):
    pass

class DatabaseConnectionError(OptiStackException):
    pass

class ExperimentNotFoundError(OptiStackException):
    pass

class ExperimentExecutionError(OptiStackException):
    pass

class InvalidDatabaseTypeError(OptiStackException):
    pass

class BenchmarkError(OptiStackException):
    pass

class ConfigurationError(OptiStackException):
    pass

