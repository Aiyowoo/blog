import logging
import logging.handlers
from queue import Queue
from os import path, mkdir


LOG_DIR = '.logs'


if not path.exists(LOG_DIR):
    mkdir(LOG_DIR)


simpleFormatter = logging.Formatter('%(asctime)s %(filename)s \
%(levelname)s %(message)s')
detailedFormatter = logging.Formatter('%(asctime)s %(filename)s \
%(fileno)d %(levelname)s %(message)s')

queue = Queue()
queueHandler = logging.handlers.QueueHandler(queue)
queueHandler.setLevel(logging.INFO)
queueHandler.setFormatter(simpleFormatter)

fileHandler = logging.handlers.RotatingFileHandler(path.join(LOG_DIR,
                                                             'blog.log'),
                                                   maxBytes=(10 * 1024 *
                                                             1024),
                                                   backupCount=5)
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(simpleFormatter)

criticalFileHandler = logging.FileHandler(path.join(LOG_DIR,
                                                    'critical.log'))
criticalFileHandler.setLevel(logging.CRITICAL)
criticalFileHandler.setFormatter(detailedFormatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(queueHandler)
logger.addHandler(criticalFileHandler)

queueListener = logging.handlers.QueueListener(queue, fileHandler,
                                               respect_handler_level=True)
