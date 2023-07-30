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

    def __init__(self, input_path='input/', output_path='output/', conf='conf/inspecting.yml'):
        self.input_path = input_path
        self.output_path = output_path

        with open(conf, 'r') as file:
            self.data = yaml.safe_load(file)['data_config']

    def find_files(self, path, ext):
        """
        Find all csvs in input folder
        """
        try:
            csv_files = glob.glob(os.path.join(path, f'*.{ext}'))
            if not csv_files:
                raise FileNotFoundError(
                    "No CSV files found in the specified directory.")
            return csv_files
        except OSError as e:
            print(f"Error reading directory: {e}")

    def set_input_files(self):
        self.input_files = self.find_files(self.input_path, 'csv')

    def map_df(self, df: pd.DataFrame, compare_df: pd.DataFrame, to_replace: str,
               replacement_col: str, reference_col: str
               ):
        """
        This function replaces values in 'df' based on a mapping defined in 'compare_df'. 
        'reference_col' is the column in 'df' that is compared with the columns in 'compare_df'.
        If a match is found, the corresponding value in 'to_replace' column is replaced using the mapping from 'compare_df'.
        """
        for compare in df[reference_col].unique():
            if compare in compare_df.columns:
                compare_mapping = compare_df.set_index(
                    compare)[replacement_col].to_dict()
                condition = df[reference_col] == compare
                df.loc[condition, to_replace] = df.loc[condition,
                                                       to_replace].replace(compare_mapping)
        return df

    def standardize_files(self, dictionary_dir='dictionary/', reference='portals', standard='standard'):
        """
        Standardize input files, add standardized file objects.
        
        Parameters:
        - dictionary_dir: Path to the directory containing dictionary CSV files.
        - reference: Column name in the input data to be used as a reference for standardization.
        - standard: Column name in the dictionary data that contains the standard values.
        """
        # Get dictionary files
        dict_files = self.find_files(dictionary_dir, 'csv')

        # Get input files
        input_files = self.input_files

        # Iterate over each input file
        for input_file in input_files:
            df = pd.read_csv(input_file)

            # Apply each dictionary to the input file
            for dict_file in dict_files:
                # Get category to replace from dictionary filename
                replacement_category = os.path.basename(os.path.splitext(dict_file)[0])

                # Load dictionary data
                compare_df = pd.read_csv(dict_file)

                # Apply mapping to the data
                df = self.map_df(df, compare_df, replacement_category, standard, reference)

            # Add standardized DataFrame to 'modified' attribute
            if not hasattr(self, 'modified'):
                self.modified = {}

            # Prepare modified dictionary name
            modified_dict_name = f"{os.path.basename(os.path.splitext(input_file)[0])}-modified"
            
            self.modified[modified_dict_name] = df
