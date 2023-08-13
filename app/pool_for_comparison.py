import yaml
import os
import pandas as pd
import json


class pool_for_comparison:
    def __init__(self, conf: str):
        with open(conf, 'r') as f:
            file = yaml.safe_load(f)
        with open(file['product_tree'], 'r') as f:
            self.product_tree = json.load(f)
        self.pair_file = file['pair_file_dest'] +  (file['product_tree'].split('.')[0]).split('/')[-1]
        self.pair_file = self.pair_file + '_match.csv'
        self.schema = file['schema']
        # pivot defines where the tree splits to reveal the dimensions we're trying to compare
        self.pivot = file['pivot']

    def get_keys_within_key(self, d, target_key):
        """
        Get all keys within a specific key of a nested dictionary. 
        This gathers keys from all instances of the target key across the tree.
        
        :param d: The nested dictionary.
        :param target_key: The key within which to get the keys.
        :return: A set of keys within the target key or an empty set if the key is not found.
        """
        # If the current object is not a dictionary, return an empty set.
        if not isinstance(d, dict):
            return set()
        
        # If the target key exists in the current dictionary, retrieve its keys.
        keys = set(d[target_key].keys()) if target_key in d and isinstance(d[target_key], dict) else set()
        
        # Recurse deeper to find other instances of the target key and aggregate the results.
        for key in d:
            keys |= self.get_keys_within_key(d[key], target_key)
        
        return keys

    def create_pair_file(self):
        if not os.path.exists(self.pair_file):

            # create a column for each unique pivot
            split_columns = self.get_keys_within_key(self.product_tree, self.pivot['pivot'])
            split_columns = sorted([f"{x}_{self.pivot['pivot_unique']}" for x in split_columns])
            cols = self.schema[:self.schema.index(self.pivot['pivot'])]
            cols = cols + split_columns
            # create dataframe
            df = pd.DataFrame({key: {} for key in cols})
            # write
            df.to_csv(self.pair_file, index=False)

        self.pair_df = pd.read_csv(self.pair_file)
