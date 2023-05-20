# flake8: noqa
PREFIX = """Answer the following question in Chinese as best you can. You have access to the following tools:"""
FORMAT_INSTRUCTIONS = """Use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
```

When you have a response, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```
"""
SUFFIX = """Begin!

Question: {input}
Thought:{agent_scratchpad}"""