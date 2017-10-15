import logging

logger = None

def init(args: dict):
    global logger
    logging.basicConfig(**args)
    logger = logging.getLogger(__name__)

def log(message: str, level: str = 'info'):
    global logger
    if (logger == None):
        init({
            'filename': 'newsCraw.log',
            'filemode': 'a',
            'format': '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S',
            'level': logging.INFO
        })
    {
        'info': logger.info,
        'debug': logger.debug,
    }[level](message)

    if True:
        print ('Logger.{}: {}'.format(level, message))
