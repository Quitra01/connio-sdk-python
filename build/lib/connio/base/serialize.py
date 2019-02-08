import datetime
import json

from connio.base import values


def iso8601_date(d):
    """
    Return a string representation of a date that the Connio API understands
    Format is YYYY-MM-DD. Returns None if d is not a string, datetime, or date
    """
    if d == values.unset:
        return d
    elif isinstance(d, datetime.datetime):
        return str(d.date())
    elif isinstance(d, datetime.date):
        return str(d)
    elif isinstance(d, str):
        return d


def iso8601_datetime(d):
    """
    Return a string representation of a date that the Connio API understands
    Format is YYYY-MM-DD. Returns None if d is not a string, datetime, or date
    """
    if d == values.unset:
        return d
    elif isinstance(d, datetime.datetime) or isinstance(d, datetime.date):
        return d.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif isinstance(d, str):
        return d


def prefixed_collapsible_map(m, prefix):
    """
    Return a dict of params corresponding to those in m with the added prefix
    """
    if m == values.unset:
        return {}

    def flatten_dict(d, result={}, prv_keys=[]):
        for k, v in d.items():
            if isinstance(v, dict):
                flatten_dict(v, result, prv_keys + [k])
            else:
                result['.'.join(prv_keys + [k])] = v

        return result

    if isinstance(m, dict):
        flattened = flatten_dict(m)
        return {'{}.{}'.format(prefix, k): v for k, v in flattened.items()}

    return {}


def object(obj):
    """
    Return a jsonified string represenation of obj if obj is jsonifiable else
    return obj untouched
    """
    if isinstance(obj, dict) or isinstance(obj, list):
        return json.dumps(obj)
    return obj


def map(lst, serialize_func):
    """
    Applies serialize_func to every element in lst
    """
    if not isinstance(lst, list):
        return lst
    return [serialize_func(e) for e in lst]


def measurement(measurement):
    """
    Serialize a measurement object to measurement JSON
    :param measurement: PropertyInstance.Measurement
    :return: jsonified string represenation of obj 
    """    
    if measurement is values.unset or measurement is None:
        return None
    return { 'type': measurement.type, 'unit': { 'label': measurement.unit.label, 'symbol': measurement.unit.symbol } }


def location(loc):
    """
    
    """    
    if loc is None:
        return None
    if loc.get('zone') is None and loc.get('geo') is not None: 
        return { 'zone': None, 'geo': loc['geo'] }
    elif loc.get('geo') is None and loc.get('zone') is not None: 
        return { 'zone': loc['zone'], 'geo': None }
    else: 
        return { 'zone': loc['zone'], 'geo': loc['geo'] }


def methodImplementation(body, lang='javascript'):
    """
    Serialize a method implementation object to JSON
    :param measurement: MethodInstance.MethodImplementation
    :return: jsonified string represenation of obj 
    """    
    if body is None:
        return None
    return { 'funcBody': body, 'script': lang }