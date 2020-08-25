import logging
from logging import handlers

level_relations = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'crit': logging.CRITICAL
}


def get_logger(name,
               filename,
               level='info',
               when='H',
               backCount=72,
               fmt='%(asctime)s - %(pathname)s - %(levelname)s: %(message)s'):
    logger = logging.getLogger(name)
    format_str = logging.Formatter(fmt)
    logger.setLevel(level_relations.get(level))
    sh = logging.StreamHandler()
    sh.setFormatter(format_str)
    th = handlers.TimedRotatingFileHandler(
        filename=filename, when=when, backupCount=backCount, encoding='utf-8')
    th.setFormatter(format_str)
    logger.addHandler(sh)
    logger.addHandler(th)
    return logger


if __name__ == '__main__':
    all_logger = get_logger(__name__+'_info', './log/all.log', level='debug')
    all_logger.debug('debug')
    # error_logger = get_logger('./log/error.log', level='error')
    # for i in range(10000):
    #     all_logger.debug('debug')
    #     all_logger.info('info')
    #     all_logger.warning('warning')
    #     all_logger.error('error')
    #     all_logger.critical('critical')
    #     error_logger.error('error')
    #     error_logger.critical('critical')
    # Logger('./log/error.log', level='error').logger.error('error2')
