from uglygpt.base import config, logger, Fore
from uglygpt.chains import LLMChain
from uglygpt.prompts import PromptTemplate

PROMPT = """
你是一个群管理员。你需要判断群里的聊天的人是否很着急或很生气（有很大的情绪），如果是的话，你需要及时通知群管理员。

群里的聊天内容如下：
{dialog}

请问你需要通知群管理员吗？如果需要，请输入“是”，否则输入“否”，然后说出谁在闹情绪，闹情绪的原因。
"""

prompt = PromptTemplate(input_variables=["dialog"], template=PROMPT)
llm_chain = LLMChain(prompt=prompt)


with open(config.workspace_path+"/chat/5.txt", "r", encoding="utf-8") as f:
    dialog = f.read()

inputs = [dialog[i:i+1000] for i in range(0, len(dialog), 1000)]
for input in inputs:
    logger.info(input, "聊天内容：", Fore.GREEN)
    output = llm_chain.run(dialog=input)
    logger.info(output,"判断结果：", Fore.GREEN)