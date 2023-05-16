import re
from colorama import Fore

from uglygpt.base import config, logger

TASK_CREATION_TEMPLATE = """
You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}.
{additional_constraints}
The last completed task has the result: {result}.
This result was based on this task description: {task}.
These are incomplete tasks: {tasks}.
Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks.Return one task per line in your response. The result must be a numbered list in the format:

1. First task
2. Second task

The number of each entry must be followed by a period. If your list is empty, write "There are no tasks to add at this time."
Unless your list is empty, do not include any headers before your numbered list or follow your numbered list with any other output."""

PRIORITY_TEMPLATE = """
You are an task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task}.
{additional_constraints}
Consider the ultimate objective of your team:{objective}.
Tasks should be sorted from highest to lowest priority, where higher-priority tasks are those that act as pre-requisites or are more essential for meeting the objective.
Do not remove any tasks. Return the result as a numbered list in the format:

1. First task
2. Second task

The entries must be consecutively numbered, starting with 1. The number of each entry must be followed by a period.
Do not include any headers before your ranked list or follow your list with any other output."""

EXECUTE_TEMPLATE = """
You are an AI who performs one task based on the following objective: {objective}.

You have the following constraints:
1. ~500 word limit for short term memory. Your short term memory is short, so immediately save important information to files.
2. If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.
3. No user assistance.

{additional_constraints}
Your task: {task}
{commands_template}
RESPOND IN THE FOLLOWING JSON FORMAT ONLY! THERE ARE SERIOUS CONSEQUENCES FOR BREAKING THIS RULE!

{
    "plan": "Your plan for achieving the task",
    "response": "Your response to the task"{commands_format}
}"""

COMMANDS_TEMPLATE = """
You have the following commands available to complete this task given. Exclusively use the commands listed in double quotes e.g. "command name"
{COMMANDS}

"""

COMMANDS_FORMAT_TEMPLATE = """,
    "command": {
        "command_name": {
            "arg1": "val1",
            "arg2": "val2"
        }
    }
"""

class AgentPrompt():
    def __init__(self):
        self.language_prompt = ""
        self.objective = ""
        self.additional_constraints = ""

    def __call__(self, type: str, **kwargs):
        match type:
            case "task":
                prompt = TASK_CREATION_TEMPLATE
            case "priority":
                prompt = PRIORITY_TEMPLATE
            case "execute":
                prompt = EXECUTE_TEMPLATE
                if "COMMANDS" in kwargs.keys() and len(kwargs["COMMANDS"])>0:
                    prompt = self._custom_format(prompt, commands_template = COMMANDS_TEMPLATE, commands_format = COMMANDS_FORMAT_TEMPLATE)
                else:
                    prompt = self._custom_format(prompt, commands_template = "", commands_format = "")
            case _:
                raise ValueError(f"Unknown type {type}")
        prompt = self._custom_format(
            prompt, objective=self.objective, additional_constraints = self.additional_constraints, **kwargs)
        if config.llm_provider != "gpt4free":
            logger.debug(prompt, "\nAgent Prompt:\n", Fore.CYAN)
        self.additional_constraints = ""
        self.add(self.language_prompt)
        return prompt

    def add(self, data: str = ""):
        if data != "":
            self.additional_constraints += data + "\n"

    def set_objective(self, objective: str):
        self.objective = objective

    def set_language(self, language: str):
        self.language_prompt = f"You must answer in the '{language}' language. If the answer is not in the '{language}' language, you need to translate it in the '{language}' language." if language != "English" else ""
        self.add(self.language_prompt)


    def _custom_format(self, string, **kwargs):
        if isinstance(string, list):
            string = "".join(str(x) for x in string)

        def replace(match):
            key = match.group(1)
            value = kwargs.get(key, match.group(0))
            if isinstance(value, list):
                return "".join(str(x) for x in value)
            else:
                return str(value)

        pattern = r"(?<!{){([^{}\n]+)}(?!})"
        result = re.sub(pattern, replace, string)
        return result
