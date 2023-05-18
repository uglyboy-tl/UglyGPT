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

from uglygpt.prompts.base import BasePromptTemplate
from uglygpt.prompts.output_parsers.list import NumberedListOutputParser

class TaskCreationPromptTemplate(BasePromptTemplate):
    def __init__(self):
        self.input_variables = ["objective", "result", "task", "tasks"]
        self.template = TASK_CREATION_TEMPLATE
        self.output_parser = NumberedListOutputParser()

    def format(self, **kwargs):
        prompt = self.format_prompt(**kwargs)
        prompt += self.output_parser.get_format_instructions()
        return prompt

class TaskPriorityPromptTemplate(BasePromptTemplate):
    def __init__(self):
        self.input_variables = ["objective", "task"]
        self.template = PRIORITY_TEMPLATE
        self.output_parser = NumberedListOutputParser()

    def format(self, **kwargs):
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