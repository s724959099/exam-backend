"""
use loguru package for logging
Ref:
    https://cuiqingcai.com/7776.html
    https://blog.csdn.net/mouday/article/details/88560543
"""

import datetime
import logging
import os

import pytz
from config import env
from loguru import logger

upload_path = '/tmp/logs'
if not os.path.exists(upload_path):
    os.mkdir(upload_path)

tz = pytz.timezone('Asia/Taipei')


class InterceptHandler(logging.Handler):
    """get all logger message including default fastapi log"""

    def emit(self, record):
        """
        Args:
            record: logging record
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """setting up all log to loguru"""
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel('INFO')

    # remove every other logger's handlers
    # and propagate to root logger
    # noinspection PyUnresolvedReferences
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


fmt = (
    'env:%%% <green>'
    '{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    '<cyan>{name}</cyan>:'
    '<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
    '<level>{message}</level>'
).replace('%%%', env)

logger.add(
    f'/tmp/logs/{datetime.datetime.now(tz):%Y%m%d}.log',
    rotation='1 week',
    retention='7 days',
    level='INFO',
    filter=lambda record: record['extra'].get('name') is None,
)
