from copy import copy
from re import compile, escape


class TemplexException(Exception):
    pass


class KeyNotFound(TemplexException):
    pass


def escape_to_regex(text):
    escaped = ""
    for character in text:
        if character == r" ":
            escaped += r" "
        else:
            escaped += escape(character)
    #if flexible_whitespace:
        #escaped = sub("\s+", "\s+", escaped)
    return escaped


DELIMETER_REGEX = compile(
    escape("{{") + r'(.*?)' + escape("}}")
)


class TemplexMatch(object):
    def __init__(self, **variables):
        self._variables = variables
    
    def __getitem__(self, key):
        return self._variables[key]


class Templex(object):
    def __init__(self, template):
        self._template = template
        self._variables = None
    
    def with_vars(self, **variables):
        new_templex = copy(self)
        new_templex._variables = variables
        return new_templex
    
    
    def match(self, string):
        is_plain_text = True
        compiled_regex = r""
        
        for chunk in DELIMETER_REGEX.split(self._template):
            if is_plain_text:
                compiled_regex = compiled_regex + escape_to_regex(chunk)
            else:
                stripped_chunk = chunk.strip()
                if stripped_chunk in self._variables.keys():
                    compiled_regex = r"{0}{1}".format(
                        compiled_regex,
                        r"(?P<{0}>{1})".format(stripped_chunk, self._variables[stripped_chunk]),
                    )
                else:
                    raise KeyNotFound("'{0}' not found in keys")
            is_plain_text = not is_plain_text

        match_obj = compile(compiled_regex).match(string)
        return TemplexMatch(**match_obj.groupdict()) if match_obj else None
