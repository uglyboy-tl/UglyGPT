from pydantic import BaseModel
from loguru import logger

from core import LLM, Model

def llm(model: Model | None = None):
    if model:
        llm = LLM(model=model)
    else:
        llm = LLM()
    logger.info(llm("你是谁？"))

def prompt(model: Model | None = None):
    if model:
        llm = LLM("{cite} 的市长是谁？", model)
    else:
        llm = LLM()
    logger.info(llm("上海"))

def instructor(model: Model | None = None):
    class UserDetail(BaseModel):
        name: str
        age: int

    if model:
        llm = LLM(model=model, response_model=UserDetail)
    else:
        llm = LLM(response_model=UserDetail)
    logger.info(llm("Extract Jason is 25 years old"))

if __name__ == "__main__":
    #llm(Model.YI)
    #llm(Model.GLM3)
    #llm(Model.QWEN)
    #llm(Model.GPT3_TURBO)
    #llm(Model.COPILOT3_TURBO)
    prompt(Model.YI)
    #instructor(Model.YI)