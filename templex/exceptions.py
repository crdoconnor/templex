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
    def __init__(self, actual, template):
        self.actual = actual
        self.template = template

    def __unicode__(self):
        return u"ACTUAL:\n{0}\n\nEXPECTED:\n{1}".format(
            self.actual.decode('utf8'),
            self.template.decode('utf8'),
        )
