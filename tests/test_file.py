import unittest
from pathlib import Path
from uglygpt.base.file import File

class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_data = "This is a test file."

    def test_save_and_load(self):
        # Test saving and loading a file
        filename = "test_file.txt"
        File.save(filename, self.test_data)
        loaded_data = File.load(filename)
        self.assertEqual(loaded_data, self.test_data)

    def test_save_with_existing_directory(self):
        # Test saving a file with an existing directory
        directory = "existing_directory"
        filename = "test_file.txt"
        file_path = Path(File.WORKSPACE_ROOT) / directory / filename

        # Create the existing directory
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the file
        File.save(str(file_path), self.test_data)

        # Check if the file exists
        self.assertTrue(file_path.exists())

        # Clean up
        file_path.unlink()
        file_path.parent.rmdir()

    def test_load_nonexistent_file(self):
        # Test loading a nonexistent file
        filename = "nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            File.load(filename)

if __name__ == '__main__':
    unittest.main()
