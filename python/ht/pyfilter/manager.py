
import argparse
import logging
import json

import ht.utils

from ht.pyfilter.logger import logger

class PyFilterManager(object):

    def __init__(self):
	self._data = {}
	self._operations = []

	self.registerOperations()

	self._parsePyFilterArgs()


    @property
    def data(self):
	return self._data

    @property
    def operations(self):
	return self._operations


    def registerOperations(self):

	import hou

	files = hou.findFiles("pyfilter/operations.json")

	for filepath in files:
	    with open(filepath) as fp:
		data = json.load(fp, object_hook=ht.utils.convertFromUnicode)

	    if "operations" not in data:
		continue

	    for operation in data["operations"]:
		module_name, class_name = operation

		cls = getattr(__import__(module_name, {}, {}, [class_name]), class_name)

		logger.info("Registering {}".format(class_name))
		self.operations.append(cls())


    def _registerParserArgs(self, parser):
	for operation in self.operations:
	    operation.registerParserArgs(parser)

    def _processParsedArgs(self, filter_args):
	for operation in self.operations:
	    operation.processParsedArgs(filter_args)

    def _parsePyFilterArgs(self):

	parser = _buildParser()

	self._registerParserArgs(parser)

	filter_args = parser.parse_known_args()[0]

	# Since the log level argument is a string we should get the
	# corresponding enum from the module and set the log level using it.
	logger.setLevel(getattr(logging, filter_args.logLevel))

	self._processParsedArgs(filter_args)

    def execute(self, stage):
	for operation in self.operations:
	    if not operation.shouldRun():
		continue

	    try:
		func = getattr(operation, stage)

	    except AttributeError:
		continue

	    func()

def _buildParser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-logLevel",
        action="store",
        default="INFO",
        choices=("CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"),
        help="The Python logging level"
    )

    return parser

