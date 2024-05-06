from celery import Celery
import logging
from flask import Flask
from typing import Any


def make_celery(app: Flask) -> Celery:
    """
    Create and configure a Celery object with Flask application context and
    custom logging.

    Args:
        app (Flask): The Flask application instance to integrate with Celery.

    Returns:
        Celery: A configured Celery instance with Flask application context
        and logging.
    """
    celery = Celery(
        app.import_name,
        backend=app.config['RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        # Ensuring connection retries on startup
        broker_connection_retry_on_startup=True
    )
    celery.conf.update(app.config)

    # Set up Celery logging
    if not celery.conf.get('worker_hijack_root_logger', False):
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    class ContextTask(celery.Task):
        """
        A Celery Task that runs within the Flask application context.
        """

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            """
            Execute the task within the Flask application context.

            Args:
                *args (Any): Variable length argument list.
                **kwargs (Any): Arbitrary keyword arguments.

            Returns:
                Any: The result of the task execution.
            """
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
