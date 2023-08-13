import os
from app.pool_for_comparison import pool_for_comparison
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import json


class TestSetupComparison(unittest.TestCase):
    def setUp(self):
        self.test_obj = pool_for_comparison(
            conf='app/tests/resources/pool_for_comparison.yml')

    def test_create_pair_file(self):
        test_df = pd.read_csv('app/tests/resources/compare/farfetch_mini_ounass_mini_match.csv')
        self.test_obj.create_pair_file()
        print(self.test_obj.pair_df, test_df)
        assert_frame_equal(self.test_obj.pair_df, test_df, check_dtype=False)
        try:
            os.remove('app/tests/resources/output/farfetch_mini_ounass_mini_match.csv')
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
