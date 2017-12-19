# -*- coding: utf-8 -*-
class TemplexException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.message


class KeyNotFound(TemplexException):
    pass


class MustUseString(TemplexException):
    """
    Must use string with templex (i.e. not bytes).
    """
    pass
