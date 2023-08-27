import yaml
import os
import pandas as pd
import json
import numpy as np
from app.helpers import get_keys_within_key, find_level, count_children, get_grouping


class ComparePool:
    def __init__(self, group, group_name):
        self.group = group
        self.group_name = group_name
        # Extract the first and second keys of the group
        group_keys = list(self.group.keys())
        self.first_group_key, self.second_group_key = group_keys[0], group_keys[1] if len(
            group_keys) > 1 else None
        self.matched = []

    def select_compare_a(self):
        """
        Selects an item from the first key in the group dictionary 
        and assigns it to the compare_a attribute.
        """
        if not self.group:
            print('The group is empty.')
            return

        first_group_values = self.group[self.first_group_key]

        if first_group_values:
            product_a_key = next(iter(first_group_values))
            self.compare_a = {product_a_key: first_group_values[product_a_key]}
        else:
            print('No more keys to compare in the first group.')

    def select_compare_b(self):
        if len(self.group[self.second_group_key]) > 0:
            self.product_b_list = self.group[self.second_group_key]
        else:
            print('No more keys to compare in the first group.')

    def select_next_a(self):
        if len(self.group[self.first_group_key]) <= 1:
            print('None to select next')
        else:
            first_group = self.group[self.first_group_key]
            keys = list(first_group.keys())
            start_key = list(self.compare_a.keys())[0]
            start_index = keys.index(start_key)
            max_index = len(keys) - 1 if keys else None
            if start_index == max_index:
                product_a_key = next(iter(first_group))
            else:
                product_a_key = keys[start_index + 1]

            self.compare_a = {product_a_key: first_group[product_a_key]}

    def select_match(self, product_name):
        """
        If the product_name exists in product_b_list, pop the value and 
        a value from compare_a, then append both to the matched list.
        """
        # Check for product_name in product_b_list
        if product_name not in self.product_b_list:
            print('Object not found in list')
            return

        # Pop the corresponding values
        key_from_compare_a = next(iter(self.compare_a))
        value_from_compare_a = self.group[self.first_group_key].pop(
            key_from_compare_a)
        value_from_product_b_list = self.product_b_list.pop(product_name)

        # Construct the matched item and append to the matched list
        matched_item = {
            self.first_group_key: {key_from_compare_a: value_from_compare_a},
            self.second_group_key: {product_name: value_from_product_b_list}
        }
        self.matched.append(matched_item)

        self.select_compare_a()

    def return_pairs(self):
        unmatched = {self.first_group_key: self.group[self.first_group_key],
                     self.second_group_key: self.group[self.second_group_key]}

        return {'matched': self.matched, 'unmatched': unmatched}


class PoolForComparison:
    def __init__(self, conf: str):
        with open(conf, 'r') as f:
            file = yaml.safe_load(f)
        with open(file['product_tree'], 'r') as f:
            self.product_tree = json.load(f)
        self.pair_file = file['pair_file_dest'] + \
            (file['product_tree'].split('.')[0]).split('/')[-1]
        self.pair_file = self.pair_file + '_match.csv'
        self.schema = file['schema']
        # pivot defines where the tree splits to reveal the dimensions we're trying to compare
        self.pivot = file['pivot']

        # get the pivot columns for comparing pairs
        self.identifiers = sorted(list(get_keys_within_key(
            self.product_tree, self.pivot['pivot'])))
        self.split_columns = sorted(
            [f"{x}_{self.pivot['pivot_unique']}" for x in self.identifiers])

    def create_pair_file(self):
        if not os.path.exists(self.pair_file):

            # create a column for each unique pivot
            cols = self.schema[:self.schema.index(self.pivot['pivot'])]
            cols = cols + self.split_columns
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
        # Fetch all unpaired items
        self.get_unpaired()

        # Start with the root of the product tree
        data = self.product_tree

        # Navigate through the product tree using the group name
        for key in group_name.split('.'):
            data = data[key]

        # Initialize an empty dictionary for the group
        group = {}

        # Populate the group dictionary with relevant data based on the pivot key
        for key in data.keys():
            group[key] = data[key][self.pivot['pivot_unique']]

        # Return the constructed group
        return group

    def select_group_name(self):
        self.get_unpaired()
        if len(list(self.describe_unpaired.keys())) > 0:
            self.group_name_selected = sorted(
                list(self.describe_unpaired.keys()))[0]
        else:
            print('No more unpaired')

    def select_next_group_name(self):
        if len(list(self.describe_unpaired.keys())) <= 1 or self.group_name_selected is None:
            self.select_group_name()
        else:
            keys = sorted(list(self.describe_unpaired.keys()))
            start_key = self.group_name_selected
            start_index = keys.index(start_key)
            max_index = len(keys) - 1 if keys else None
            if start_index == max_index:
                selected = next(iter(self.describe_unpaired))
            else:
                selected = keys[start_index + 1]

            self.group_name_selected = selected

    def start_compare_pool(self, group_name):
        group = self.fetch_unpaired_group(group_name)
        self.comparepool = ComparePool(group, group_name)

    def get_matched_from_pool(self):
        return self.comparepool.return_pairs()

    def set_up_matched(self):
        if os.path.exists(self.pair_file):
            self.matched_df = pd.read_csv(self.pair_file)
            self.matched = []
        else:
            self.matched = []
            self.matched_df = pd.DataFrame(columns=self.schema)

    def update_matched(self):
        matched = self.get_matched_from_pool()
        if matched not in self.matched:
            matched = {self.comparepool.group_name: matched}
            self.matched.append(matched)

    def rework_to_pair_file(self, match_dict: list):
        # given match output from ComparePool reformat to add to match file
        'crawl_date.2023-06-18.country.sa.gender.women.brand.KENZO.category.shoes.site'
        match_name = list(match_dict.keys())[0]
        split = match_name.split('.')
        # get values
        values = [item for index, item in enumerate(
            split[:-1]) if index % 2 != 0]
        reworked = []
        # add matched self.split_columns
        for match in match_dict[match_name]['matched']:
            col = values + [list(match[self.identifiers[0]].keys())[0],
                            list(match[self.identifiers[1]].keys())[0]]
            reworked.append(col)
        unmatched1 = list(match_dict[match_name]
                          ['unmatched'][self.identifiers[0]].keys())
        [reworked.append(values + [x] + [None]) for x in unmatched1]
        unmatched2 = list(match_dict[match_name]
                          ['unmatched'][self.identifiers[1]].keys())
        [reworked.append(values + [None] + [x]) for x in unmatched2]

        return pd.DataFrame(reworked, columns=self.pair_df.columns)

    def consolidate_matched(self):
        for match in self.matched:
            # rework pair file entries from group name
            reworked = self.rework_to_pair_file(match)
            # add matched and unmatched
            for index, row in reworked.iterrows():
                # if matched, i.e. both rows are available
                if row[self.split_columns[0]] and row[self.split_columns[1]]:
                    # drop all rows in pair_file that had one of these values
                    self.pair_df = self.pair_df[self.pair_df[self.split_columns[0]]
                                                != row[self.split_columns[0]]]
                    self.pair_df = self.pair_df[self.pair_df[self.split_columns[1]]
                                                != row[self.split_columns[1]]]
                    self.pair_df = self.pair_df.reset_index(drop=True)
                    self.pair_df.loc[self.pair_df.index.max()+1] = row
                elif row[self.split_columns[0]] and row[self.split_columns[0]] not in self.pair_df[self.split_columns[0]].values:
                    self.pair_df.loc[self.pair_df.index.max()+1] = row
                elif row[self.split_columns[1]] and row[self.split_columns[1]] not in self.pair_df[self.split_columns[1]].values:
                    self.pair_df.loc[self.pair_df.index.max()+1] = row
        # update consolidated 
        self.pair_df = self.pair_df.drop_duplicates(
            keep='first').reset_index(drop=True)
        # reset matched to blank
        self.matched = []

    def save_pair_df(self):
        self.pair_df.to_csv(self.pair_file, index=False)
