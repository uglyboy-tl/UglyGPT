import os
import unittest
from uglygpt.base.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Set up any necessary configurations or environment variables before each test case
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        os.environ["OPENAI_API_BASE"] = "test_api_base"
        os.environ["LLM_PROVIDER"] = "test_llm_provider"

    def tearDown(self):
        # Clean up any configurations or environment variables after each test case
        os.environ.pop("OPENAI_API_KEY")
        os.environ.pop("OPENAI_API_BASE")
        os.environ.pop("LLM_PROVIDER")

    def test_singleton(self):
        # Ensure that the Config class is a singleton
        config1 = Config()
        config2 = Config()
        self.assertIs(config1, config2)

    def test_default_values(self):
        # Ensure that the default values are set correctly
        config = Config()
        self.assertEqual(config.BASE_LOG_DIR, "logs")
        self.assertEqual(config.openai_api_key, "test_api_key")
        self.assertEqual(config.openai_api_base, "test_api_base")
        self.assertEqual(config.llm_provider, "test_llm_provider")

    def test_environment_variables_override_defaults(self):
        # Ensure that environment variables override the default values
        os.environ["OPENAI_API_KEY"] = "new_api_key"
        os.environ["OPENAI_API_BASE"] = "new_api_base"
        os.environ["LLM_PROVIDER"] = "new_llm_provider"

        config = Config()
        self.assertEqual(config.openai_api_key, "new_api_key")
        self.assertEqual(config.openai_api_base, "new_api_base")
        self.assertEqual(config.llm_provider, "new_llm_provider")

    def test_missing_environment_variables(self):
        # Ensure that missing environment variables fall back to the default values
        os.environ.pop("OPENAI_API_KEY")
        os.environ.pop("OPENAI_API_BASE")
        os.environ.pop("LLM_PROVIDER")

        config = Config()
        self.assertEqual(config.openai_api_key, "test_api_key")
        self.assertEqual(config.openai_api_base, "test_api_base")
        self.assertEqual(config.llm_provider, "test_llm_provider")

if __name__ == "__main__":
    unittest.main()
