import os, time
from typing import Dict, Any
from uglygpt.base import config, logger, Fore
from uglygpt.chains.map_reduce.base import AnalyzeDocumentChain
from uglygpt.chains import LLMChain
from uglygpt.prompts import PromptTemplate
from uglygpt.text_splitter import RecursiveCharacterTextSplitter
from uglygpt.provider.llm.openai import tiktoken_len

#config.set_debug_mode(True)

from pydub import AudioSegment
speech = AudioSegment.from_file(os.path.join(config.workspace_path,"speech/speech.m4a"), format="m4a")
speech.export(os.path.join(config.workspace_path,"speech/speech.wav"), format="wav")

from uglygpt.provider.speech_recognizer.azure import AzureSpeechRecongnizerProvider
speech_recognizer = AzureSpeechRecongnizerProvider()
document = speech_recognizer.recognition(os.path.join(config.workspace_path,"speech1.wav"))

with open(os.path.join(config.workspace_path,"speech/speech.txt"), "w", encoding="utf-8") as f:
    f.write(document)

splitter = RecursiveCharacterTextSplitter(
    separators=["\n", "。", "？", "！"],
    chunk_size=2000,
    chunk_overlap=0,
    length_function=tiktoken_len,
)
content = list(splitter.split_text(document))

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
llm_chain = LLMChain(prompt=PromptTemplate(input_variables=["text"], template=TEMPLATE))
chain =AnalyzeDocumentChain(map_chain=llm_chain)

T1 = time.time()
outputs = chain({"input_documents":content})
T2 = time.time()
logger.info(f"{T2-T1:.2f}s", "Time Cost:" ,Fore.GREEN)
logger.info(outputs["output"], "Entities:", Fore.GREEN)

with open(os.path.join(config.workspace_path,"speech/speech_fix.txt"), "w", encoding="utf-8") as f:
    f.write(outputs["output"])
