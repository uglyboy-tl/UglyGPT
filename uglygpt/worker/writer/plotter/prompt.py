SYNOPSIS = """Brainstorm an extremely long complete, detailed synopsis for a story with the following appeal terms:

{input}

Extremely long and highly detailed complete plot synopsis with beginning, middle, and end.
Translate the output into Chinese if it is not already in Chinese.

BEGINNING:"""

TITLE = """Come up with the perfect title for the following premise.  The title should be pithy, catchy, and memorable.
Translate the title into Chinese if it is not already in Chinese.

PREMISE: {synopsis}

UNIQUE PERFECT TITLE:
"""

THEME = """Describe the theme of the following story in a few sentences. What is the universal truth elucidated by this story?
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

UNIVERSAL TRUTH:
"""

THEME_LIGHT = """What is the light side of the following universal truth? Write an essay on the topic.

UNIVERSAL TRUTH: {theme}

LIGHT SIDE ESSAY:
"""

THEME_DARK = """What is the dark side of the following universal truth? Write an essay on the topic.

UNIVERSAL TRUTH: {theme}

DARK SIDE ESSAY:
"""

THEME_UNDERSTAND = """What are some ways that someone can misunderstand or misapply this universal truth? What are some different perspectives? Write an essay on the topic.

UNIVERSAL TRUTH: {theme}

MISUNDERSTAND ESSAY:
"""

SETTING = """Use your imagination to brainstorm details about the setting. Think about history, culture, atmosphere, religion, politics, and so on.
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

BRAINSTORM SETTING IDEAS:
"""

CHARACTER = """Brainstorm original characters for the following story. List names, backstories, and personalities. Vividly depict all characters. Invent names if necessary.
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

UNIVERSAL TRUTH: {theme}

LIST OF CHARACTERS:
"""

OUTLINE = """Brainstorm a highly detailed plot outline with at least 12 plot beats. List all the story beats in sequence and describe each plot element with a few sentences.
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

THEME: {theme}

CHARACTERS:
{characters}

LONG DETAILED PLOT OUTLINE:
"""
