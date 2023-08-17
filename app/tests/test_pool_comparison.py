import os
from app.pool_for_comparison import PoolForComparison, ComparePool
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import json


class TestSetupComparison(unittest.TestCase):
    def setUp(self):
        self.test_obj = PoolForComparison(
            conf='app/tests/resources/pool_for_comparison.yml')

        with open('app/tests/resources/json/test_fetch_unpaired_group_mini.json') as f:
            compare = json.load(f)

        self.test_compare = ComparePool(
            compare, 'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site')

    def test_create_pair_file(self):
        test_df = pd.read_csv(
            'app/tests/resources/compare/farfetch_mini_ounass_mini_match.csv')
        self.test_obj.create_pair_file()
        assert_frame_equal(self.test_obj.pair_df, test_df, check_dtype=False)
        try:
            os.remove(
                'app/tests/resources/output/farfetch_mini_ounass_mini_match.csv')
        except FileNotFoundError:
            pass

    def test_get_unpaired(self):
        compare = {'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site': {'Farfetch.product_name': 33,
                                                                                                     'Ounass.product_name': 7},
                   'crawl_date.2023-06-18.country.sa.gender.women.brand.Burberry.category.shoes.site': {'Farfetch.product_name': 26,
                                                                                                        'Ounass.product_name': 9}}
        self.test_obj.get_unpaired()
        self.assertEqual(self.test_obj.describe_unpaired, compare)

    def test_fetch_unpaired_group(self):
        asserted_pair = self.test_obj.fetch_unpaired_group(
            'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site')
        with open('app/tests/resources/json/test_fetch_unpaired_group.json') as f:
            compare = json.load(f)
        self.assertEqual(asserted_pair, compare)

    def test_select_compare_a(self):
        self.test_compare.select_compare_a()
        to_assert = {
            "panelled-design sneakers": {
                "text": "['panelled-design sneakers', 'FARFETCH ID: ', 'Brand style ID: ']"
            }}
        self.assertEqual(self.test_compare.compare_a, to_assert)


if __name__ == '__main__':
    unittest.main()
