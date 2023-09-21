import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

from uglygpt.base.file import File

class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_data = "This is a test data"
        self.filename = "test_file.txt"
        self.file_path = Path.cwd() / self.filename

    def tearDown(self):
        if self.file_path.exists():
            self.file_path.unlink()

    def test_save(self):
        File.save(self.filename, self.test_data)

        self.assertTrue(self.file_path.exists())
        with open(self.file_path, "r") as f:
            saved_data = f.read()
        self.assertEqual(saved_data, self.test_data)

    def test_load(self):
        with open(self.file_path, "w") as f:
            f.write(self.test_data)

        loaded_data = File.load(self.filename)

        self.assertEqual(loaded_data, self.test_data)

    @patch('uglygpt.base.file.datetime')
    def test_backup(self, mock_datetime):
        self.file_path.touch()
        mock_datetime.now.return_value = datetime(2022, 1, 1, 12, 0, 0)
        backup_path = self.file_path.with_name(self.file_path.stem + '_20220101120000.txt.bak')

        File._backup(self.file_path)

        self.assertTrue(backup_path.exists())
        backup_path.unlink()

if __name__ == '__main__':
    unittest.main()
