import yaml
import os
import pandas as pd
import json
from app.helpers import get_keys_within_key, find_level, count_children, get_grouping


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

    def create_pair_file(self):
        if not os.path.exists(self.pair_file):

            # create a column for each unique pivot
            split_columns = get_keys_within_key(self.product_tree, self.pivot['pivot'])
            split_columns = sorted([f"{x}_{self.pivot['pivot_unique']}" for x in split_columns])
            cols = self.schema[:self.schema.index(self.pivot['pivot'])]
            cols = cols + split_columns
            # create dataframe
            df = pd.DataFrame({key: {} for key in cols})
            # write
            df.to_csv(self.pair_file, index=False)
        # load pair file if it exists
        if not hasattr(self, 'pair_df'):
            self.pair_df = pd.read_csv(self.pair_file)
        else:
            print('pair file already exists and loaded')
        
    def load_pair_file(self):
        if not self.pair_df:
            self.pair_df = pd.read_csv(self.pair_file)
        else:
            print('pair file already exists and loaded')
    
    def get_unpaired(self):
        # find tree level of product
        level = find_level(self.product_tree, self.pivot['pivot'], 1) + 2
        # get number of children
        children_count = count_children(self.product_tree, 1, level)
        # get number of unpaired in each level
        grouping = get_grouping(children_count, self.pivot['pivot'])
        self.describe_unpaired = grouping

    def fetch_unpaired_group(self, group_name):
        self.get_unpaired()
        data = self.product_tree
        for key in group_name.split('.'):
            data = data[key]
        
        group = {}
        for key in data.keys():
            group[key] = data[key][self.pivot['pivot_unique']]
            
        return group
    


    
    

