from uglygpt.base import config, logger, Fore
from uglygpt.chains import LLMChain
from uglygpt.prompts import PromptTemplate

# The prompt is a template string that will be filled in with the input variables.
PROMPT = """
你是一个群管理员。你需要判断群里的聊天的人是否很着急或很生气（有很大的情绪），如果是的话，你需要及时通知群管理员。

群里的聊天内容如下：
{dialog}

请问你需要通知群管理员吗？如果需要，请输入“是”，否则输入“否”，然后说出谁在闹情绪，闹情绪的原因。
"""

# The prompt is initialized with the template and the input variables. The
# prompt will be automatically filled in with the input variables before each
# generation.
prompt = PromptTemplate(input_variables=["dialog"], template=PROMPT)

# The LLMChain object handles the entire generation process, including
# generating a prompt, running the model, and returning the most likely
# continuation.
llm_chain = LLMChain(prompt=prompt)

# Read in the chat data.
with open(config.workspace_path+"/chat/5.txt", "r", encoding="utf-8") as f:
    dialog = f.read()

# Split the data into smaller chunks so that each chunk is a reasonable size
# for a single generation.
inputs = [dialog[i:i+1000] for i in range(0, len(dialog), 1000)]

# Generate a continuation for each chunk of input data.
for input in inputs:
    logger.info(input, "聊天内容：", Fore.GREEN)
