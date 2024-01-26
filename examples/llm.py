from enum import Enum, unique

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
    @unique
    class Gender(Enum):
        FEMALE = "FEMALE"
        MALE = "MALE"

    class UserDetail(BaseModel):
        name: str
        gender: Gender

    if model:
        llm = LLM(model=model, response_model=UserDetail)
    else:
        llm = LLM(response_model=UserDetail)
    logger.info(llm("Extract Jason is a boy"))

if __name__ == "__main__":
    #llm(Model.YI)
    #llm(Model.GLM3)
    #llm(Model.QWEN)
    #llm(Model.GPT3_TURBO)
    #llm(Model.COPILOT3_TURBO)
    prompt(Model.YI)
    #instructor(Model.YI)