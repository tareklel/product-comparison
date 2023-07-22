import os
from app.setup_comparison import setup_comparison
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal


class TestSetupComparison(unittest.TestCase):
    def setUp(self):
        self.test_obj = setup_comparison()

    def test_read_files(self):
        expected_csv_files = [
            'input/farfetch-2023-06-18.csv',
            'input/ounass-2023-06-18.csv'
        ]

        # Test the read_files method
        self.test_obj.find_files('input/', 'csv')

        # Check if the CSV files list matches the expected list
        self.assertEqual(self.test_obj.csv_files, expected_csv_files)

    def test_map_df(self):
        """
        test map_df
        """
        df = {'names': ['betty', 'jeff'],
                 'company': ['x', 'y']
                 }
        compare_df = {'x': ['betty', 'jeff'],
                     'standard': ['beatrice', 'jeffrey']}
        expected = {'names': ['beatrice', 'jeff'],
                    'company': ['x', 'y']
                    }
        df = pd.DataFrame(df)
        compare_df = pd.DataFrame(compare_df)
        expected = pd.DataFrame(expected)

        mapped = self.test_obj.map_df(df, compare_df,
                        'names', 'standard', 'company')
        assert_frame_equal(mapped, expected)


if __name__ == '__main__':
    unittest.main()
