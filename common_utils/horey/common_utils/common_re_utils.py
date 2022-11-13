"""
Some reusable stuff.
"""
import datetime
import importlib
import os
import sys

import re


class CommonREUtils:
    """
    Some stuff to be reused
    """

    _FIRST_CAP_RE = None
    _ALL_CAP_RE = None

    @property
    def first_cap_re(self):
        if CommonREUtils._FIRST_CAP_RE is None:
            CommonREUtils._FIRST_CAP_RE = re.compile("(.)([A-Z][a-z]+)")
        return CommonREUtils._FIRST_CAP_RE

    @property
    def all_cap_re(self):
        if CommonREUtils._ALL_CAP_RE is None:
            CommonREUtils._ALL_CAP_RE = re.compile("([a-z0-9])([A-Z])")
        return CommonREUtils._ALL_CAP_RE

    def pascal_case_case_to_snake_case(self, name):
        """
        # shamelessly copied from https://stackoverflow.com/a/1176023
        format_attr_name('CamelCase')
        'camel_case'
        format_attr_name('CamelCamelCase')
        'camel_camel_case'
        format_attr_name('Camel2Camel2Case')
        'camel2_camel2_case'
        format_attr_name('getHTTPResponseCode')
        'get_http_response_code'
        format_attr_name('get2HTTPResponseCode')
        'get2_http_response_code'
        format_attr_name('HTTPResponseCode')
        'http_response_code'
        format_attr_name('HTTPResponseCodeXYZ')
        'http_response_code_xyz'
        :param name:
        :return:
        """

        s1 = self.first_cap_re.sub(r"\1_\2", name)
        s1 = s1.replace("__", "_")
        return self.all_cap_re.sub(r"\1_\2", s1).lower()
