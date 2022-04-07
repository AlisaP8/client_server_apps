import inspect
import logging
import sys
import traceback


if sys.argv[0].find('client') == -1:
    log = logging.getLogger('server')
else:
    log = logging.getLogger('client')


class Log:
    def __call__(self, func):
        def log_saver(*args, **kwargs):
            res = func(*args, **kwargs)
            log.debug(f'Вызов функции: {func.__name__} с параметрами {args}, {kwargs}.'
                      f'Модуль: {func.__module__}.'
                      f'Вызов из функции {traceback.format_stack()[0].strip().split()[-1]}.'
                      f'Вызов из функции {inspect.stack()[1][3]}')
            return res
        return log_saver


# def logger(func):
#     def log_saver(*args, **kwargs):
#         log_name = 'server' if 'server.py' in sys.argv[0] else 'client'
#         log = logging.getLogger(log_name)
#
#         res = func(*args, **kwargs)
#         log.debug(f'Функция: {func.__name__}.'
#                   f'Парамаетры: {args}, {kwargs}.'
#                   f'Модуль: {func.__module__}.'
#                   f'Вызов из функции: {traceback.format_stack()[0].strip().split()[-1]}.'
#                   f'Вызов из функции: {inspect.stack()[1][3]}')
#         return res
#     return log_saver
