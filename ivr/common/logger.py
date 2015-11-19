# -*- coding: utf-8 -*-
import logging
import logging.config


def default_config(debug=False):
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s [%(process)d] [%(name)s] [%(levelname)s] - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
    logging.config.dictConfig(log_config)
