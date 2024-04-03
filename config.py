# config.py is a module that defines configuration classes for the application.
class BaseConfig:
    """
    A class representing the base configuration for the application.

    Attributes:
        REQUEST_TIMEOUT (int): Default request timeout in seconds.
        Used to define how long the application waits for a response.
    """
    REQUEST_TIMEOUT: int = 3


class ProdConfig(BaseConfig):
    """
    Represents production configuration.

    Inherits from BaseConfig with production-specific settings.

    Attributes:
        REQUEST_TIMEOUT (int): Higher request timeout for production.
    """
    REQUEST_TIMEOUT: int = 10


class TestConfig(BaseConfig):
    """
    Represents test configuration.

    Inherits BaseConfig, adjusting settings for test use.

    Attributes:
        REQUEST_TIMEOUT (int): Timeout for test environment.
    """
    REQUEST_TIMEOUT: int = 5
