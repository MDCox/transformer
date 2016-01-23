import arrow
import datetime
import dateutil.parser

import collections
import re


class APIError(Exception):
    """ Base Exception for the API """
    status_code = 400

    def __init__(self, message, status_code=500, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv


def tdelta(input_):
    """
    convert a human readable time delta into a dictionary that can be used
    to create an actual time delta object or other method for manipulating a
    date

    """
    keys = ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds']

    delta = collections.OrderedDict()
    for key in keys:
        matches = re.findall('((?:-\s*)?\d+)\s?{}?'.format(key), input_)
        if not matches:
            delta[key] = 0
            continue
        for m in matches:
            delta[key] = int(m) if m else 0
    return delta


def try_parse_date(date_value, from_format=None):
    """
    try to parse a int or string value into a datetime format

    """
    try:
        # check to see if the string can be converted into a float (a timestamp)
        try:
            date_value = float(date_value)
        except:
            pass

        # if this is a unix string... or a milliseconds since epoch
        if isinstance(date_value, int) or isinstance(date_value, long) or isinstance(date_value, float):
            if date_value >= (1 << 32) - 1:
                date_value /= 1000.0
            return datetime.datetime.fromtimestamp(date_value)

        # otherwise, try to parse the date value from the from_format
        if from_format:
            dt = arrow.get(date_value, from_format)
            if dt:
                return dt
    except:
        pass

    # otherwise, use the fuzzy parser
    return dateutil.parser.parse(date_value, fuzzy=True)


def import_submodules(package_name):
    """ Import all submodules of a module, recursively

    :param package_name: Package name
    :type package_name: str
    :rtype: dict[types.ModuleType]
    """
    import importlib
    import pkgutil
    import sys
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + '.' + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    }
