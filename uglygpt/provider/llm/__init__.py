from uglygpt.provider.llm.base import LLMProvider
from uglygpt.base import config, logger

supported_llm_providers = []

try:
    from uglygpt.provider.llm.openai import OpenAILLM
    supported_llm_providers.append(OpenAILLM)
except ImportError:
    print("OpenAILLM not installed. Skipping import.")
    OpenAILLM = None

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
            print(
                "Error: OpenAILLM is not installed. Please install openai"
                " to use OpenAI as a LLM provider."
            )
        else:
            return OpenAILLM()
    elif llm_provider_name == "gpt4free":
        return None
    elif llm_provider_name == "huggingchat":
        return None
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