
# Standard Library Imports
from functools import wraps

from ht.pyfilter.logger import logger


import mantra

class PyFilterOperation(object):

    def __init__(self):
        self._data = {}

    def __repr__(self):
	return "<PyFilterOperation: {}>".format(
	    self.__class__.__name__
	)

    @property
    def data(self):
        return self._data


    @staticmethod
    def registerParserArgs(parser):
        pass

    def processParsedArgs(filter_args):
        pass

    def shouldRun(self):
        return True


def logFilter(method_or_name):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            class_name = args[0].__class__.__name__

            msg = "{}.{}()".format(class_name, func_name)

            if isinstance(method_or_name, str):
                msg = "{} ({})".format(
                    msg,
                    mantra.property(method_or_name)[0]
                )

            logger.debug(msg)

            func(*args, **kwargs)

        return wrapper

    if callable(method_or_name):

        return decorator(method_or_name)

    return decorator

