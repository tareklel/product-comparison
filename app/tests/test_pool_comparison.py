import os
from app.pool_for_comparison import PoolForComparison, ComparePool
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import json
import io
import sys


class TestSetupComparison(unittest.TestCase):
    def setUp(self):
        self.test_obj = PoolForComparison(
            conf='app/tests/resources/pool_for_comparison.yml')

        with open('app/tests/resources/json/test_fetch_unpaired_group_mini.json') as f:
            compare = json.load(f)
    
        try:
            os.remove(
                'app/tests/resources/output/farfetch_mini_ounass_mini_match.csv')
        except FileNotFoundError:
            pass

        self.test_compare = ComparePool(
            compare, 'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site')

    def test_select_compare_a(self):
        self.test_compare.select_compare_a()
        to_assert = {
            "panelled-design sneakers": {
                "text": "['panelled-design sneakers', 'FARFETCH ID: ', 'Brand style ID: ']"
            }}
        self.assertEqual(self.test_compare.compare_a, to_assert)

    def test_select_compare_b(self):
        self.test_compare.select_compare_b()
        to_assert = {
            "Kenzoschool Boke Flower Slip-on Sneakers in Canvas": {
                "text": "An iconic sneaker that evokes the designer's Japanese heritage with a signature boke flower that decorates the upper proudly. Crafted from canvas, the slip-on silhouette are topped with elasticated sides which make them easy to put on and slide off,. "
            },
            "Kenzoschool High-top Sneakers in Canvas": {
                "text": "Kenzo's high-top sneakers reference retro-skate culture. Crafted in Thailand, the sneakers are set on a graphic rubber sole and have a canvas upper with BOKE FLOWER embroidery and a military-inspired tag engraved with the address of Kenzo's Paris headquarters."
            }
        }
        self.assertEqual(self.test_compare.product_b_list, to_assert)

    def test_select_match(self):
        # Select the first comparison group for testing
        self.test_compare.select_compare_a()

        # Select the second comparison group for testing
        self.test_compare.select_compare_b()

        # Perform a match for the specified product name
        self.test_compare.select_match(
            'Kenzoschool Boke Flower Slip-on Sneakers in Canvas')

        # Define the expected matched output
        test = [{'Farfetch': {
            "panelled-design sneakers": {
                "text": "['panelled-design sneakers', 'FARFETCH ID: ', 'Brand style ID: ']"
            }}, 'Ounass': {
            "Kenzoschool Boke Flower Slip-on Sneakers in Canvas": {
                "text": "An iconic sneaker that evokes the designer's Japanese heritage with a signature boke flower that decorates the upper proudly. Crafted from canvas, the slip-on silhouette are topped with elasticated sides which make them easy to put on and slide off,. "
            }}}]

        # Assert that the matching is as expected
        self.assertEqual(self.test_compare.matched, test)

        # Define the expected dictionary after a product has been removed
        reduced_test = {"Kenzoschool High-top Sneakers in Canvas": {
            "text": "Kenzo's high-top sneakers reference retro-skate culture. Crafted in Thailand, the sneakers are set on a graphic rubber sole and have a canvas upper with BOKE FLOWER embroidery and a military-inspired tag engraved with the address of Kenzo's Paris headquarters."
        }}

        # Check if the dictionary has been reduced as expected
        self.assertEqual(self.test_compare.product_b_list, reduced_test)

        # Define the expected state of the first comparison group after matching
        self.assertEqual(self.test_compare.compare_a, {"Kenzoschool high-top sneakers": {
            "text": "['Kenzoschool high-top sneakers', \"Balancing exuberant detailing with streetwear comfort, these high-top sneakers work to capture Kenzo's fun-loving aesthetic. Ridged rubber detailing completes the design, while the brand's signature embroidered Boke Flower motif lends a playful feel.\", 'FARFETCH ID: ', 'Brand style ID: ']"
        }})

        # Confirm the state of the second comparison group remains consistent
        self.assertEqual(self.test_compare.product_b_list, {"Kenzoschool High-top Sneakers in Canvas": {
            "text": "Kenzo's high-top sneakers reference retro-skate culture. Crafted in Thailand, the sneakers are set on a graphic rubber sole and have a canvas upper with BOKE FLOWER embroidery and a military-inspired tag engraved with the address of Kenzo's Paris headquarters."
        }})

        # Redirect stdout to a buffer to capture printed output
        buffer = io.StringIO()
        sys.stdout = buffer

        # Attempt another match which should result in no more keys
        self.test_compare.select_match(
            'Kenzoschool High-top Sneakers in Canvas')

        # Assert that the printed message matches our expectation
        self.assertEqual(buffer.getvalue(),
                         'No more keys to compare in the first group.\n')

    def test_return_pairs(self):
        # Select the first comparison group for testing
        self.test_compare.select_compare_a()

        # Select the second comparison group for testing
        self.test_compare.select_compare_b()

        # Perform a match for the specified product name
        self.test_compare.select_match(
            'Kenzoschool Boke Flower Slip-on Sneakers in Canvas')

        with open('app/tests/resources/json/test_return_pairs.json') as f:
            compare = json.load(f)

        matched = self.test_compare.return_pairs()
        self.assertEqual(matched, compare)

    def test_select_next_a(self):
        self.test_compare.select_compare_a()
        self.test_compare.select_next_a()

        test = {
            "Kenzoschool high-top sneakers": {
                "text": "['Kenzoschool high-top sneakers', \"Balancing exuberant detailing with streetwear comfort, these high-top sneakers work to capture Kenzo's fun-loving aesthetic. Ridged rubber detailing completes the design, while the brand's signature embroidered Boke Flower motif lends a playful feel.\", 'FARFETCH ID: ', 'Brand style ID: ']"
            }
        }

        self.assertEqual(self.test_compare.compare_a, test)

        self.test_compare.select_next_a()

        test2 = {
            "panelled-design sneakers": {
                "text": "['panelled-design sneakers', 'FARFETCH ID: ', 'Brand style ID: ']"
            }
        }
        self.assertEqual(self.test_compare.compare_a, test2)
    
    # TEST PoolForComparison

    def test_create_pair_file(self):
        test_df = pd.read_csv(
            'app/tests/resources/compare/farfetch_mini_ounass_mini_match.csv')
        self.test_obj.create_pair_file()
        assert_frame_equal(self.test_obj.pair_df, test_df, check_dtype=False)

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

    def test_select_group_name(self):

        self.test_obj.select_group_name()
        self.assertEqual(self.test_obj.group_name_selected,
                         'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site')

    def test_select_group_name(self):
        self.test_obj.select_group_name()
        self.test_obj.select_next_group_name()
        self.assertEqual(self.test_obj.group_name_selected, 'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site'
                         )
        self.test_obj.select_next_group_name()
        self.assertEqual(self.test_obj.group_name_selected,
                         'crawl_date.2023-06-18.country.sa.gender.women.brand.Burberry.category.shoes.site')
        
    def test_set_up_matched(self):
        self.test_obj.set_up_matched()
        df = pd.DataFrame(columns=self.test_obj.schema)
        assert_frame_equal(self.test_obj.matched_df, df)
        pd.DataFrame(columns=['b']).to_csv(self.test_obj.pair_file)
        del self.test_obj.matched_df
        with self.assertRaises(ValueError) as context:
            self.test_obj.set_up_matched()
        
        self.assertEqual(str(context.exception), 'Schema and file columns do not match')

    def test_update_matched(self):
        self.test_obj.set_up_matched()
        self.test_obj.comparepool = self.test_compare
        self.test_obj.comparepool.select_compare_a()
        self.test_obj.comparepool.select_compare_b()
        self.test_obj.comparepool.select_match(
            'Kenzoschool Boke Flower Slip-on Sneakers in Canvas')
        self.test_obj.update_matched()
        with open('app/tests/resources/json/test_return_pairs.json') as f:
            d = json.load(f)
        compare = {'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site' : d}
        self.assertEqual(self.test_obj.matched, [compare])

    def test_consolidated_matched(self):
        self.test_obj.pair_file = 'app/tests/resources/compare/farfetch_mini_ounass_mini_match.csv'
        self.test_obj.comparepool = self.test_compare
        self.test_obj.comparepool.select_compare_a()
        self.test_obj.comparepool.select_compare_b()
        self.test_obj.comparepool.select_match(
            'Kenzoschool Boke Flower Slip-on Sneakers in Canvas')
        self.test_obj.consolidate_matched()
        # we need to check if pair_file is updated
        df = pd.read_csv('app/tests/resources/compare/test_consolidate_matched.csv')
        self.test_obj.consolidated_matched()
        assert_frame_equal(self.test_obj.matched_df, df)
        
        


if __name__ == '__main__':
    unittest.main()
    
    try:
        os.remove(
            'app/tests/resources/output/farfetch_mini_ounass_mini_match.csv')
    except FileNotFoundError:
        pass
