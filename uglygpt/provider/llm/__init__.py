from uglygpt.provider.llm.base import LLMProvider
from uglygpt.base import config, logger

supported_llm_providers = []

try:
    from uglygpt.provider.llm.openai import OpenAILLM
    supported_llm_providers.append(OpenAILLM)
except ImportError:
    logger.warn("OpenAILLM not installed. Skipping import.")
    OpenAILLM = None

try:
    from uglygpt.provider.llm.huggingchat import HuggingChatLLM
    supported_llm_providers.append(HuggingChatLLM)
except ImportError:
    logger.warn("HuggingChatLLM not installed. Skipping import.")
    HuggingChatLLM = None


def get_llm_provider(llm_provider_name: str = None) -> LLMProvider:
    llm_provider_name = llm_provider_name or config.llm_provider
    """
    Get the LLM provider.

    Args:
        llm_provider_name: str

    Returns: LLMProvider
    """

    if llm_provider_name == "openai":
        if not OpenAILLM:
            logger.error(
                "Error: OpenAILLM is not installed. Please install openai"
                " to use OpenAI as a LLM provider."
            )
        else:
            return OpenAILLM()
    elif llm_provider_name == "gpt4free":
        return None
    elif llm_provider_name == "huggingchat":
        if not HuggingChatLLM:
            logger.error(
                "Error: HuggingChatLLM is not installed. Please install huggingface"
                " to use HuggingChat as a LLM provider."
            )
        return HuggingChatLLM()
    elif llm_provider_name == "huggingface":
        return None
    elif llm_provider_name == "bard":
        return None
    elif llm_provider_name == "palm":
        return None
    elif llm_provider_name == "fastchat":
        return None
    else:
        logger.error("LLM provider not implemented")
        raise NotImplementedError("LLM provider not implemented")