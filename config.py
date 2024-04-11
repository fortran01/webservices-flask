# config.py is a module that defines configuration classes for the application.
class BaseConfig:
    """
    A class representing the base configuration for the application.

    Attributes:
        REQUEST_TIMEOUT (int): Default request timeout in seconds.
        Used to define how long the application waits for a response.
        LONGPOLL_TIMEOUT (int): Default long poll timeout in seconds.
    """
    REQUEST_TIMEOUT: int = 3
    LONGPOLL_TIMEOUT: int = 30


class ProdConfig(BaseConfig):
    """
    Represents production configuration.

    Inherits from BaseConfig with production-specific settings.

    Attributes:
        REQUEST_TIMEOUT (int): Higher request timeout for production.
        Inherits LONGPOLL_TIMEOUT from BaseConfig unless overridden.
    """
    REQUEST_TIMEOUT: int = 10
    # LONGPOLL_TIMEOUT is inherited from BaseConfig


class TestConfig(BaseConfig):
    """
    Represents test configuration.

    Inherits BaseConfig, adjusting settings for test use.

    Attributes:
        REQUEST_TIMEOUT (int): Timeout for test environment.
        Inherits LONGPOLL_TIMEOUT from BaseConfig unless overridden.
    """
    REQUEST_TIMEOUT: int = 5
    # LONGPOLL_TIMEOUT is inherited from BaseConfig
