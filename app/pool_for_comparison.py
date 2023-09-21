import yaml
import os
import pandas as pd
import json
import numpy as np
from app.helpers import get_keys_within_key, find_level, count_children, get_grouping, df_to_nested_dict, remove_from_tree


class ComparePool:
    def __init__(self, group, group_name, *args):
        self.group = group
        self.group_name = group_name
        self.initialize_keys()
        self.args = args
        self.matched = []

    def initialize_keys(self):
        """Initialize the first and second keys from the group dictionary."""
        group_keys = list(self.group.keys())
        self.first_group_key = group_keys[0]
        self.second_group_key = group_keys[1] if len(group_keys) > 1 else None

    def select_compare_a(self):
        """Select an item from the first key and store it in compare_a attribute."""
        self.select_item_for_comparison(self.first_group_key, 'compare_a')

    def select_item_for_comparison(self, key_name, attr_name):
        """Helper method to select an item for comparison."""
        if not self.group or not self.group[key_name]:
            print(f'No more keys to compare in the first group.')
            return
        item_key = next(iter(self.group[key_name]))
        setattr(self, attr_name, {item_key: self.group[key_name][item_key]})

    def select_compare_b(self):
        """Select items from the second key and store them in product_b_list attribute."""
        self.product_b_list = self.group[self.second_group_key] if self.group[self.second_group_key] else None

    def select_next_a(self):
        """Select the next item in the first group for comparison."""
        self.select_next_item_for_comparison(self.first_group_key, 'compare_a')

    def select_next_item_for_comparison(self, key_name, attr_name):
        """Helper method to select the next item for comparison."""
        if not self.group[key_name] or len(self.group[key_name]) <= 1:
            print('None to select next')
            return

        keys = list(self.group[key_name].keys())
        start_key = list(getattr(self, attr_name).keys())[0]
        start_index = keys.index(start_key)

        # Get the next key
        next_key = keys[(start_index + 1) % len(keys)]
        setattr(self, attr_name, {next_key: self.group[key_name][next_key]})

    def select_match(self, product_name):
        """Identify and store matched items."""
        if product_name not in self.product_b_list:
            print('Object not found in list')
            return
        self.store_matched_item(product_name)

    def store_matched_item(self, product_name):
        """Helper method to store matched items."""
        key_from_compare_a = next(iter(self.compare_a))
        value_from_compare_a = self.group[self.first_group_key].pop(
            key_from_compare_a)
        value_from_product_b_list = self.product_b_list.pop(product_name)

        matched_item = {
            self.first_group_key: {key_from_compare_a: value_from_compare_a},
            self.second_group_key: {product_name: value_from_product_b_list}
        }
        self.matched.append(matched_item)

        # Select the next 'a' for further comparison
        self.select_compare_a()

    def return_pairs(self):
        """Return both matched and unmatched items."""
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
        print(self.pair_file)
        self.schema = file['schema']
        # pivot defines where the tree splits to reveal the dimensions we're trying to compare
        self.pivot = file['pivot']
        self.file = file
        self.matched = []

        # get the pivot columns for comparing pairs
        self.identifiers = sorted(list(get_keys_within_key(
            self.product_tree, self.pivot['pivot'])))
        self.split_columns = sorted(
            [f"{x}_{self.pivot['pivot_unique']}" for x in self.identifiers])

    def create_pair_file(self):
        """ Create a CSV file to store product pairings if it doesn't exist """
        if not os.path.exists(self.pair_file):

            # create a column for each unique pivot
            cols = self.schema[:self.schema.index(self.pivot['pivot'])]
            cols = cols + self.split_columns
            # create dataframe
            df = pd.DataFrame({key: {} for key in cols})
            # write
            df.to_csv(self.pair_file, index=False)
        # load pair file if it exists
        self.load_pair_file()

    def load_pair_file(self):
        if not hasattr(self, 'pair_df'):
            self.pair_df = pd.read_csv(self.pair_file)
            self.pair_df[self.split_columns] = self.pair_df[self.split_columns].astype(str)
        else:
            print('pair file already exists and loaded')

    def matched_to_singles(self):
        """turns matched pairs from matched_df into tree"""
        # turn pair_df to adhere to self.schema
        # get only matched from pair_df
        matched = self.pair_df[(self.pair_df[self.split_columns[0]].notna()) & (
            self.pair_df[self.split_columns[1]].notna())]
        # get matched_df for matched to first
        matched1 = matched[[
            x for x in matched.columns if x != self.split_columns[1]]]
        matched1[self.pivot['pivot']] = self.identifiers[0]
        matched1 = matched1.rename(
            {self.split_columns[0]: self.pivot['pivot_unique']}, axis=1)
        for col in [col for col in self.schema if col not in matched1.columns]:
            matched1[col] = np.nan
        matched1 = matched1[self.schema]
        matched2 = matched[[
            x for x in matched.columns if x != self.split_columns[0]]]
        matched2[self.pivot['pivot']] = self.identifiers[1]
        matched2 = matched2.rename(
            {self.split_columns[1]: self.pivot['pivot_unique']}, axis=1)
        for col in [col for col in self.schema if col not in matched2.columns]:
            matched2[col] = np.nan
        matched2 = matched2[self.schema]
        matched1 = pd.concat([matched1, matched2]).reset_index(drop=True)

        return matched1

    def matched_to_tree(self):
        """turns matched to singles and then to tree"""
        matched_split = self.matched_to_singles()
        return df_to_nested_dict(matched_split, self.schema)

    def remove_matched_from_tree(self):
        if not self.pair_df.empty:
            matched = self.matched_to_tree()
            print(matched)
            target_level = find_level(self.product_tree, self.pivot['pivot_unique']) + 1
            remove_from_tree(self.product_tree, matched, 1 ,target_level)
        else:
            print('pair_df is empty')

    def get_unpaired(self):
        """Get group names + Calculate the number of unpaired products at each level in the product tree"""
        # find tree level of product
        level = find_level(self.product_tree, self.pivot['pivot'], 1) + 2
        # get number of children
        children_count = count_children(self.product_tree, 1, level)
        # get number of unpaired in each level
        grouping = get_grouping(children_count, self.pivot['pivot'])
        self.describe_unpaired = grouping

    def fetch_unpaired_group(self, group_name):
        """Fetch all unpaired products within a specified group"""
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
        """Select first unpaired group"""
        self.get_unpaired()
        if len(list(self.describe_unpaired.keys())) > 0:
            self.group_name_selected = sorted(
                list(self.describe_unpaired.keys()))[0]
        else:
            print('No more unpaired')

    def select_next_group_name(self):
        """Select the next unpaired group after the current selection"""
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

    def start_compare_pool(self, group_name, *args):
        """Initialize comparison pool for the selected group"""
        group = self.fetch_unpaired_group(group_name)
        self.comparepool = ComparePool(group, group_name, args)

    def get_matched_from_pool(self):
        """Fetch matched pairs from the comparison pool"""
        return self.comparepool.return_pairs()

    def update_matched(self):
        """Add newly matched pairs to the matched list"""
        matched = self.get_matched_from_pool()
        if matched not in self.matched:
            matched = {self.comparepool.group_name: matched}
            self.matched.append(matched)

    def rework_to_pair_file(self, match_dict: list):
        """Reformat the matched pairs for addition to the pair file"""
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
        """Consolidate all matched pairs  and unmatched into the main pair dataframe"""
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
                    self.pair_df = self.pair_df.reset_index(drop=True)
                    self.pair_df.loc[self.pair_df.index.max()+1] = row
                elif row[self.split_columns[1]] and row[self.split_columns[1]] not in self.pair_df[self.split_columns[1]].values:
                    self.pair_df = self.pair_df.reset_index(drop=True)
                    self.pair_df.loc[self.pair_df.index.max()+1] = row
        # update consolidated
        self.pair_df = self.pair_df.drop_duplicates(
            keep='first').reset_index(drop=True)
        # reset matched to blank
        self.matched = []

    def save_pair_df(self):
        self.pair_df.to_csv(self.pair_file, index=False)
