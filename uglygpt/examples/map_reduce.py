import os, time, re
from typing import Dict, Any
from uglygpt.base import config, logger, Fore
from uglygpt.chains.map_reduce.base import AnalyzeDocumentChain
from uglygpt.chains.transform import TransformChain
from uglygpt.chains import LLMChain
from uglygpt.prompts import PromptTemplate

#config.set_debug_mode(True)

def func(inputs:Dict[str, Any]):
    inputs.update({"output":inputs.pop("input")})
    return inputs

transform_chain = TransformChain(input_variables=["input"], output_variables=["output"], transform=func)

filepath = os.path.join(config.workspace_path,"speech.txt")
with open(filepath, "r", encoding="utf-8") as f:
    document = f.read()

content = re.findall(r".{1000}", document)

TEMPLATE="""你是我的笔录员。你可以帮我整理以下的讲话稿。
要求：
1. 请保留所有讲话内容，不进行提炼;
2. 文中如果有书写错误，请帮我修改;
3. 将口语化转化为书面语，比如“嗯”、“呃”等词汇都不要了。
4. 按照意思分段;

讲话稿:
'''{text}'''

整理后:
"""
prompt = PromptTemplate(input_variables=["text"], template=TEMPLATE)
llm_chain = LLMChain(prompt=prompt)
#logger.info(llm_chain({"text":content})["data"], "Entities:", Fore.GREEN)

chain =AnalyzeDocumentChain(map_chain=llm_chain, reduce_chain=transform_chain)

T1 = time.time()
outputs = chain({"input_documents":content})
T2 = time.time()
logger.info(f"{T2-T1:.2f}s", "Time Cost:" ,Fore.GREEN)
logger.info(outputs["output"], "Entities:", Fore.GREEN)
