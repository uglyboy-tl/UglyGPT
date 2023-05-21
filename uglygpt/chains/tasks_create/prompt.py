from __future__ import annotations
TASK_CREATION_TEMPLATE = """
You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}.
The last completed task has the result: {result}.
This result was based on this task description: {task}.
These are incomplete tasks: {tasks}.
Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks.Return one task per line in your response."""

PRIORITY_TEMPLATE = """
You are an task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task}.
Consider the ultimate objective of your team: {objective}.
Tasks should be sorted from highest to lowest priority, where higher-priority tasks are those that act as pre-requisites or are more essential for meeting the objective.
Do not remove any tasks.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from uglygpt.prompts.output_parsers.base import BaseOutputParser

from uglygpt.prompts.base import BasePromptTemplate
from uglygpt.prompts.output_parsers.list import NumberedListOutputParser

@dataclass
class TaskCreationPromptTemplate(BasePromptTemplate):
    input_variables: List[str] = field(default_factory= lambda: ["objective", "result", "task", "tasks"])
    output_parser: Optional[BaseOutputParser] = field(default_factory=NumberedListOutputParser)
    template: str = TASK_CREATION_TEMPLATE

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        prompt = self.format_prompt(**kwargs)
        if "Language" in kwargs and kwargs["Language"] != "English":
            language = kwargs["Language"]
            prompt += f"\nYou must answer in the '{language}' language. If the answer is not in the '{language}' language, you need to translate it in the '{language}' language."
        prompt += self.output_parser.get_format_instructions()
        return prompt

@dataclass
class TaskPriorityPromptTemplate(BasePromptTemplate):
    input_variables: List[str] = field(default_factory= lambda: ["objective", "task"])
    output_parser: Optional[BaseOutputParser] = field(default_factory=NumberedListOutputParser)
    template: str = PRIORITY_TEMPLATE

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        prompt = self.format_prompt(**kwargs)
        prompt += self.output_parser.get_format_instructions()
        return prompt

def get_prompt(prompt_name: str) -> BasePromptTemplate:
    if prompt_name == "task_creation":
        return TaskCreationPromptTemplate()
    elif prompt_name == "task_priority":
        return TaskPriorityPromptTemplate()
    else:
        raise ValueError(f"Invalid prompt name: {prompt_name}")