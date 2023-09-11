#!/usr/bin/env python3
#-*-coding:utf-8-*-

import re
from dataclasses import dataclass

@dataclass
class Prompt(object):
    template: str = ""

    def format(self, **kwargs):
        """Format the prompt with the given kwargs."""
        def replace(match):
            key = match.group(1)
            value = kwargs.get(key, match.group(0))
            if isinstance(value, list):
                return "".join(str(x) for x in value)
            else:
                return str(value)

        pattern = r"(?<!{){([^{}\n]+)}(?!})"
        result = re.sub(pattern, replace, self.template)
        return result

    @property
    def input_variables(self):
        return re.findall(r"{([^{}\n]+)}", self.template)