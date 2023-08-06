import os
from app.setup_comparison import setup_comparison
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import json


class TestSetupComparison(unittest.TestCase):
    def setUp(self):
        self.test_obj = setup_comparison(
            conf='app/tests/resources/inspecting.yml')

        self.test_obj.nested_tree = {'country': {
            'us': {'product':
                   {'x': {'description': 'its'},
                    'y': {'description': 'a'}}},
            'uk': {'product': {'x': {'description': 'product'}}}}}

    def test_read_files(self):
        expected_csv_files = [
            'app/tests/resources/input/farfetch-2023-06-18.csv',
            'app/tests/resources/input/ounass-2023-06-18.csv'
        ]

        # Test the read_files method
        self.test_obj.set_input_files()

        # Check if the CSV file paths list matches the expected list
        self.assertEqual(sorted(self.test_obj.input_files), sorted(expected_csv_files))

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

    def test_standardize_files(self):
        self.test_obj.set_input_files()
        self.test_obj.standardize_files()
        compare1 = pd.read_csv(
            'app/tests/resources/compare/farfetch-2023-06-18.csv')
        compare2 = self.test_obj.modified['farfetch-2023-06-18-modified']
        assert_frame_equal(compare1, compare2)

    def test_find_combinations(self):
        order = ['country', 'product', 'description']
        df = pd.DataFrame({'country': ['us', 'us', 'uk'], 'product': [
                          'x', 'y', 'x'], 'description': ['its', 'a', 'product']})
        dict = {}
        tree = self.test_obj.find_combinations(order, df, dict)
        self.assertEqual(tree, self.test_obj.nested_tree)

    def test_update_json(self):
        path = 'app/tests/resources/json/test_find_combinations.json'

        with open(path, 'w') as f:
            json.dump(self.test_obj.nested_tree, f)

        test_json = {'country': {
            'us': {'product':
                   {'x': {'description': 'its'},
                    'y': {'description': 'a'}}},
            'uk': {'product': {'x': {'description': 'product'}, 'z': {'description': 'le'}}}}}

        self.test_obj.data['inspection_order'] = [
            'country', 'product', 'description']
        self.test_obj.modified = {}
        self.test_obj.modified['mod-modified'] = pd.DataFrame({'country': ['uk'], 'product': [
            'z'], 'description': ['le']})

        self.test_obj.update_json(path, True)
        with open(path, 'r') as f:
            modified_json = json.load(f)

        self.assertEqual(modified_json, test_json)

        os.remove(path)
    
    def test_create_json(self):
        self.test_obj.set_input_files()
        self.test_obj.create_json()
        test_path = 'app/tests/resources/output/farfetch-2023-06-18_ounass-2023-06-18.json'
        self.assertTrue(os.path.exists(test_path))
        os.remove(test_path)

if __name__ == '__main__':
    unittest.main()
