# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os


def get_logger(name='shootings.log', level=logging.INFO, maxbytes=1024, backupcount=5):
    print(os.getcwd())
    filename = os.path.join('..', 'logs', name)
    logger = logging.getLogger('ShootingsLogger')
    logger.setLevel(level)

    handler = logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=maxbytes,
        backupCount=backupcount
    )
    f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    handler.setFormatter(f)
    logger.addHandler(handler)

    return logger


if __name__ == '__main__':
    my_log = get_logger(maxbytes=20)
    for i in range(20):
        my_log.info('i = %d' % i)
