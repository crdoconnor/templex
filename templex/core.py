# -*- coding: utf-8 -*-
from copy import copy
from re import compile, escape
from templex.exceptions import KeyNotFound, NonMatching, MustUseString
import difflib
import sys


if sys.version_info[0] == 3:
    unicode = str


def escape_to_regex(text):
    escaped = r""
    for character in text:
        if character == r" ":
            escaped += r" "
        else:
            escaped += escape(character)
    """
    if flexible_whitespace:
        escaped = sub("\s+", "\s+", escaped)
    """
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
        if not isinstance(template, (unicode, str)) or isinstance(template, bytes):
            raise MustUseString("Must use string with templex (e.g. not bytes).")
        self._template = template
        self._variables = {}

    def with_vars(self, **variables):
        for name, variable in variables.items():
            if not isinstance(variable, (unicode, str)):
                raise MustUseString("Must use string with templex (e.g. not bytes).")
        new_templex = copy(self)
        new_templex._variables = variables
        return new_templex

    def assert_match(self, string):
        """
        Raises informative exception when string does not match the templex.
        """
        if self.match(string) is not None:
            return
        else:
            is_plain_text = True
            compiled_regex = r""
            list_of_chunks = []
            list_of_unescaped_chunks = []

            for chunk in DELIMETER_REGEX.split(self._template):
                if is_plain_text:
                    compiled_regex = compiled_regex + escape_to_regex(chunk)
                    list_of_chunks.append(escape_to_regex(chunk))
                    list_of_unescaped_chunks.append(chunk)
                else:
                    stripped_chunk = chunk.strip()
                    if stripped_chunk in self._variables.keys():
                        compiled_regex = ur"{0}{1}".format(
                            compiled_regex,
                            ur"(?P<{0}>{1})".format(
                                stripped_chunk,
                                self._variables[stripped_chunk],
                            ),
                        )
                        list_of_chunks.append(
                            r"(?P<{0}>{1})".format(stripped_chunk, self._variables[stripped_chunk])
                        )
                        list_of_unescaped_chunks.append(r"{{ " + stripped_chunk + r" }}")
                    else:
                        raise KeyNotFound((
                            "'{0}' not found in variables. "
                            "Specify with with_vars(var=regex).\n".format(
                              stripped_chunk
                            )
                        ))

                is_plain_text = not is_plain_text

            to_diff = r""
            to_compare = string
            for chunk, unescaped_chunk in zip(list_of_chunks, list_of_unescaped_chunks):
                match = compile(chunk).search(string)
                if match is not None:
                    to_diff += to_compare[match.start():match.end()]
                    to_compare = to_compare[match.end():]
                else:
                    to_diff += unescaped_chunk

            diff = ''.join(difflib.ndiff(
                string.splitlines(1),
                to_diff.splitlines(1)
            ))

            raise NonMatching(
                string,
                self._template,
                diff,
            )

    def match(self, string):
        """
        Returns TemplexMatch object if there is a match or None if there isn't.
        """
        if not isinstance(string, (unicode, str)) or isinstance(string, bytes):
            raise MustUseString("Must use string with templex (e.g. not bytes).")

        is_plain_text = True
        compiled_regex = r""

        for chunk in DELIMETER_REGEX.split(self._template):
            if is_plain_text:
                compiled_regex = compiled_regex + escape_to_regex(chunk)
            else:
                stripped_chunk = chunk.strip()
                if stripped_chunk in self._variables.keys():
                    compiled_regex = ur"{0}{1}".format(
                        compiled_regex,
                        ur"(?P<{0}>{1})".format(stripped_chunk, self._variables[stripped_chunk]),
                    )
                else:
                    raise KeyNotFound(
                        "'{0}' not found in variables. Specify with with_vars(var=regex).".format(
                          stripped_chunk
                        )
                    )
            is_plain_text = not is_plain_text

        match_obj = compile(compiled_regex).match(string)
        return TemplexMatch(**match_obj.groupdict()) if match_obj else None
