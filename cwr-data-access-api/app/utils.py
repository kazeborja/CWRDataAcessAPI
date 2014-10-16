import json
import datetime
import time


class JSONConverter(object):
    """
    JSON converter from objects and list
    """
    def list_to_json(self, elements_list):
        """
        Convert a list to its json equivalent

        :param elements_list: list of elements to be converted
        :return: json array ready be returned as string
        """
        json_result = '[\n'
        for element in elements_list:
            json_result += self.object_to_json(element) + ",\n" \
                if len(elements_list)-1 != elements_list.index(element) \
                else self.object_to_json(element) + "\n"
        json_result += "]"
        return json_result

    @staticmethod
    def object_to_json(element):
        """
        Convert a object to its json equivalent

        :param element: element to be converted
        :return: json object in string format
        """
        return json.dumps(row2dict(element))


class Struct(object):
    """
    Class to convert from dictionary to object

    :see: http://stackoverflow.com/questions/1305532/convert-python-dict-to-object/1305663#1305663
    """
    def __init__(self, **entries): 
        self.__dict__.update(entries)


class DictionaryList2ObjectList(object):
    """
    Class to convert from a list of dictionaries to a list of objects
    """
    @staticmethod
    def convert(given_list):
        """
        Convert a list of dictionaries in a list of objects

        :param given_list: list of dictionaries
        :return: list of object
        """
        returned_list = []
        for element in given_list:
            returned_list.append(Struct(**element))
        return returned_list


def check_if_date(field_name, object, row):
    """
    Convert a date field into long format

    :param field_name: name of the field where the date is
    :param object: object to store the date in long format
    :param row: object, usually a SQLAlchemy row where field is stored
    """
    if type(getattr(row, field_name)) is datetime.date or type(getattr(row, field_name)) is datetime.datetime:
        object[field_name] = time.mktime(getattr(row, field_name).timetuple())
    else:
        object[field_name] = getattr(row, field_name)


def row2dict(row):
    """
    Converts a row of SQLAlchemy into a dictionary

    :see: http://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
    :param row: SQLAlchemy row
    :return: dictionary
    """
    if row is None:
        return None
    d = {}
    if hasattr(row, '__table__'):
        for column in row.__mapper__.columns:
            check_if_date(column.name, d, row)
        if hasattr(row, 'other_parseable_fields'):
            for field in row.other_parseable_fields:
                result = is_primitive(getattr(row, field))
                if isinstance(getattr(row, field), object) and not is_primitive(getattr(row, field)):
                    d[field] = row2dict(getattr(row, field))
                else:
                    check_if_date(field, d, row)
        return d
    else:
        for column in get_user_attrs(row):
            check_if_date(column, d, row)
        return d


def get_user_attrs(object):
    """
    Return the attributes of an object

    :param object: the object to get attributes from
    :return: list of attributes
    """
    return [k for k in dir(object)
            if not k.startswith('__')
            and not k.endswith('__')]


def is_primitive(thing):
    """
    Check whether a object is of a primitive type or not

    :param thing: object to check if its type is primitive
    :return: True if it is primitive, else False
    """
    primitive = (int, str, bool, float, unicode)
    return type(thing) in primitive


def string_to_date(date_string):
    if date_string is None:
        return None
    else:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()