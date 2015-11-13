

import ast
from collections import Iterable

import mantra



class Property(object):

    def __init__(self, name):

	self._name = name
	self._value = None

	self._initData()


    def _initData(self):
	values = mantra.property(self.name)
	print values

	if len(values) == 1:
	    value = values[0]

	    if len(value.split()) > 2:
		split_vals = value.split()

		value = dict(zip(*[iter(split_vals)]*2))

	    else:
		value = _parseString(value)

	else:
	    value = values

	self._value = value


    @property
    def name(self):
	return self._name

    @property
    def value(self):
	return self._value

    @value.setter
    def value(self, value):
	if value is None:
	    value = []

	if not isinstance(value, Iterable):
	    value = [value]

	mantra.setproperty(self.name, value)
	self._initData()



def _parseString(value):

    if value.lower() == "false":
	return False

    if value.lower() == "true":
	return True

    return value

def setProperty(name, value):
    Property(name).value = value

