"""Configuration class to store the state of bools for different scripts access."""
import os
from colorama import Fore
from pathlib import Path

from uglygpt.base import Singleton

class Config(metaclass=Singleton):
    """
    Configuration class to store the state of bools for different scripts access.
    """

    def __init__(self) -> None:
        """Initialize the Config class"""
        # Workspace settings
        workspace_directory = Path(__file__).parent.parent.parent / "Data"
        self.workspace_path = str(workspace_directory)

        # Logging settings
        self.file_logger_path =  str(workspace_directory / "logs")

        # Proxy settings
        self.proxy = True
        self.proxy_url = os.getenv("PROXY_URL")
        self.proxy_port = os.getenv("PROXY_PORT")

        # Debug settings
        self.debug_mode = False

        # Language settings
        self.language = os.getenv("LANGUAGE", "English")

        # API keys
        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        # HuggingChat
        self.huggingchat_cookie = os.getenv("HF_COOKIE")
        # Google
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_project_id = os.getenv("GOOGLE_PROJECT_ID")
        self.custom_search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
        # BARD
        self.bard_token = os.getenv("BARD_TOKEN")
        # Pinecone
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_region = os.getenv("PINECONE_ENV")

        # Memory settings
        self.memory_index = os.getenv("MEMORY_INDEX", "uglygpt")
        self.memory_backend = os.getenv("MEMORY_BACKEND", "no_memory")

        # LLM settings
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.huggingface_model_path = os.getenv("HUGGINGFACE_MODEL_PATH", "HuggingFaceH4/starchat-alpha")

        # Embedding settings
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai")

    def set_openai_api_key(self, value: str) -> None:
        """Set the OpenAI API key value."""
        self.openai_api_key = value

    def set_bard_token(self, value: str) -> None:
        """Set the BARD token value."""
        self.bard_token = value

    def set_pinecone_api_key(self, value: str) -> None:
        """Set the Pinecone API key value."""
        self.pinecone_api_key = value

    def set_pinecone_region(self, value: str) -> None:
        """Set the Pinecone region value."""
        self.pinecone_region = value

    def set_debug_mode(self, value: bool) -> None:
        """Set the debug mode value."""
        self.debug_mode = value

    def set_language(self, value: str) -> None:
        """Set the language value."""
        self.language = value

    def set_llm_provider(self, value: str) -> None:
        """Set the LLM provider value."""
        self.llm_provider = value

    def set_huggingface_model_path(self, value: str) -> None:
        """Set the HuggingFace model path value."""
        self.huggingface_model_path = value

    def set_embedding_provider(self, value: str) -> None:
        """Set the embedding provider value."""
        self.embedding_provider = value

    def set_memory_backend(self, value: str) -> None:
        """Set the memory backend value."""
        self.memory_backend = value

    def start_proxy(self) -> None:
        """Start the proxy."""
        if self.proxy:
            if self.proxy_url is None or self.proxy_port is None:
                print(
                    f"{Fore.RED}ERROR: Proxy URL or Proxy Port is not set.{Fore.RESET}"
                )
                raise Exception("Proxy URL or Proxy Port is not set.")
            os.environ["HTTP_PROXY"] = self.proxy_url + ":" + self.proxy_port
            os.environ["HTTPS_PROXY"] = self.proxy_url + ":" + self.proxy_port

    def stop_proxy(self) -> None:
        """Stop the proxy."""
        if self.proxy:
            os.environ.pop("HTTP_PROXY")
            os.environ.pop("HTTPS_PROXY")

config = Config()