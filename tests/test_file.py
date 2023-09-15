import unittest
from pathlib import Path
from uglygpt.base.file import File

class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_data = "This is a test file."

    def test_save(self):
        # Test saving a file
        filename = "test_file.txt"
        File.save(filename, self.test_data)

        # Check if the file exists
        file_path = Path.cwd() / filename
        self.assertTrue(file_path.exists())

        # Check if the file content is correct
        with open(file_path, "r") as f:
            saved_data = f.read()
        self.assertEqual(saved_data, self.test_data)

    def test_load(self):
        # Create a test file
        filename = "test_file.txt"
        file_path = Path.cwd() / filename
        with open(file_path, "w") as f:
            f.write(self.test_data)

        # Test loading the file
        loaded_data = File.load(filename)

        # Check if the loaded data is correct
        self.assertEqual(loaded_data, self.test_data)

    def tearDown(self):
        # Remove the test file
        filename = "test_file.txt"
        file_path = Path.cwd() / filename
        if file_path.exists():
            file_path.unlink()

if __name__ == '__main__':
    unittest.main()
