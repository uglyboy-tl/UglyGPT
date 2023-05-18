from uglygpt.prompts.base import BasePromptTemplate

class DefaultPromptTemplate(BasePromptTemplate):
    def __init__(self):
        self.input_key = "input"
        self.template = """{input}"""

    @property
    def input_variables(self):
        return [self.input_key]

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        return self.format_prompt(**kwargs)
