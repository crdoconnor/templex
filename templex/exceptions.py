class TemplexException(Exception):
    pass


class KeyNotFound(TemplexException):
    pass


class NonMatching(TemplexException):
    pass
