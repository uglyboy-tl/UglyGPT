import unittest
import unittest.mock as mock
from unittest.mock import patch
import json
from uglygpt.actions.utils import fix_llm_json_str, parse_json, parse_code

class TestUtils(unittest.TestCase):
    def test_fix_llm_json_str_valid_json(self):
        # Test case for valid JSON input
        input_string = '{"name": "John", "age": 30}'
        expected_output = '{"name": "John", "age": 30}'
        self.assertEqual(fix_llm_json_str(input_string), expected_output)

    def test_fix_llm_json_str_invalid_json(self):
        # Test case for invalid JSON input
        input_string = '{"name": "John", "age": 30'
        expected_output = '{"name": "John", "age": 30}'
        with patch('uglygpt.actions.utils.logger') as mock_logger:
            self.assertEqual(fix_llm_json_str(input_string), expected_output)
            mock_logger.warning.assert_called_with("fix_llm_json_str failed 3:", mock.ANY)

    def test_fix_llm_json_str_json_in_code_block(self):
        # Test when the input string contains JSON in a code block
        input_string = 'Some text ```json\n{"key": "value"}\n```'
        expected_output = '\n{"key": "value"}\n'
        self.assertEqual(fix_llm_json_str(input_string), expected_output)

    def test_fix_llm_json_str_json_with_newline(self):
        # Test when the input string contains JSON with newline characters
        input_string = '{"key": "value\n"}'
        expected_output = '{"key": "value\\n"}'
        self.assertEqual(fix_llm_json_str(input_string), expected_output)

    def test_parse_json_valid_json(self):
        # Test case for valid JSON input
        input_string = '{"name": "John", "age": 30}'
        expected_output = {"name": "John", "age": 30}
        self.assertEqual(parse_json(input_string), expected_output)

    def test_parse_code_with_code_block(self):
        # Test case for code block with language specified
        input_text = 'Some text\n```python\nprint("Hello, World!")\n```'
        expected_output = 'print("Hello, World!")'
        self.assertEqual(parse_code(input_text), expected_output)

    def test_parse_code_without_code_block(self):
        # Test case for text without code block
        input_text = 'Some text without code block'
        with self.assertRaises(Exception):
            parse_code(input_text)

    def test_parse_code_with_code_block_no_language(self):
        # Test case for code block without language specified
        input_text = 'Some text\n```\nprint("Hello, World!")\n```'
        expected_output = 'print("Hello, World!")'
        self.assertEqual(parse_code(input_text), expected_output)

if __name__ == '__main__':
    unittest.main()