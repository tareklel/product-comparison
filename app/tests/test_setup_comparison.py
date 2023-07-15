import os
from app.setup_comparison import setup_comparison
import unittest


class TestSetupComparison(unittest.TestCase):
    def setUp(self):
        self.test_obj = setup_comparison()

    def test_read_files(self):
        expected_csv_files = [
            'input/farfetch-2023-06-18.csv',
            'input/ounass-2023-06-18.csv'
        ]

        # Test the read_files method
        self.test_obj.find_files()

        # Check if the CSV files list matches the expected list
        self.assertEqual(self.test_obj.csv_files, expected_csv_files)


if __name__ == '__main__':
    unittest.main()
