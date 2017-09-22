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


class NonMatching(TemplexException):
    def __init__(self, actual, template, diff):
        self.actual = actual
        self.template = template
        self.diff = diff

    def __unicode__(self):
        return u"ACTUAL:\n{0}\n\nEXPECTED:\n{1}\n\nDIFF:\n{2}".format(
            self.actual,
            self.template,
            self.diff,
        )


class MustUseString(TemplexException):
    """
    Must use string with templex (e.g. not bytes).
    """
    pass
