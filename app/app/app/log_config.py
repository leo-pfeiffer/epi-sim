from logging.config import dictConfig
from .configuration import APP_DIR
import os


def config_logger():
    """
    Configure the loggers for the application.
    This sets up a root logger with two handlers:
    - file: logs WARNING and higher to logs/app.log
    - console: logs INFO and higher to console
    """
    log_dir = f"{os.path.join(APP_DIR, 'logs', 'app.log')}"

    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s: %(module)s: %(message)s'
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': log_dir,
                'formatter': 'default',
                'level': 'WARNING'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
                'level': 'INFO'
            }
        },
        'loggers': {
            'root': {
                'handlers': ['file', 'console'],
                'level': 'INFO'
            },
        }
    })
