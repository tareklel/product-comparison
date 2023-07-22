import os
import glob
import csv
import yaml
import json
import pandas as pd


class setup_comparison:
    """
    get and organize products to compare
    """

    def __init__(self, input_path='in', output_path='output/'):
        self.input_path = input_path
        self.output_path = output_path

        with open('conf/inspecting.yml', 'r') as file:
            self.data = yaml.safe_load(file)['data_config']

    def find_files(self, path, ext):
        """
        Find all csvs in input folder
        """
        try:
            self.csv_files = glob.glob(os.path.join(path, f'*.{ext}'))
            if not self.csv_files:
                raise FileNotFoundError(
                    "No CSV files found in the specified directory.")
        except OSError as e:
            print(f"Error reading directory: {e}")

    def map_df(self, df: pd.DataFrame, compare_df: pd.DataFrame, to_replace: str,
               replacement_col: str, reference_col: str
               ):
        """

        """
        for compare in  df[reference_col].unique():
            if compare in compare_df.columns:
                compare_mapping = compare_df.set_index(compare)[replacement_col].to_dict()
                condition = df[reference_col] == compare
                df.loc[condition, to_replace] = df.loc[condition, to_replace].replace(compare_mapping)
        return df

