# import logging

# def get_logger(class_name):
#     logger = logging.getLogger(class_name)
#     logger.setLevel(logging.INFO)

#     formatter = logging.Formatter('{"time": "%(asctime)s", "class": "%(name)s", "log_level": "%(levelname)s", "log": %(message)s}')

#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.DEBUG)
#     console_handler.setFormatter(formatter)
#     logger.addHandler(console_handler)

#     return logger

import logging

class Logger():
    def get_logger(format, silent):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        if format == 'json':
            formatter = logging.Formatter('{"time": "%(asctime)s", "origin": "p%(process)s %(filename)s:%(name)s:%(lineno)d", "log_level": "%(levelname)s", "log": "%(message)s"}')
        else:
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s p%(process)s %(filename)s:%(name)s:%(lineno)d %(message)s")
        console_handler = logging.StreamHandler()

        if silent:
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler) 
        else:
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger